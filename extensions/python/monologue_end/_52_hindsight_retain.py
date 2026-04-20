"""
Hindsight Retain Extension
After the core memory plugin memorizes fragments, this extension
also retains them to Hindsight for semantic enrichment.

Runs at priority _52 (after _50_memorize_fragments and _51_memorize_solutions).
"""

import asyncio
import os
import sys
from helpers import errors, plugins
from helpers.extension import Extension
from helpers.dirty_json import DirtyJson
from agent import LoopData
from helpers.defer import DeferredTask, THREAD_BACKGROUND

# Fix import path for hindsight plugin helpers
# Add /a0 to sys.path so that 'usr.plugins.a0_hindsight' can be resolved
plugin_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if plugin_base not in sys.path:
    sys.path.insert(0, plugin_base)

from usr.plugins.a0_hindsight.helpers import hindsight_helper

class HindsightRetain(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        print("[HINDSIGHT RETAIN] _52_hindsight_retain.execute() called")
        if not self.agent:
            print("[HINDSIGHT RETAIN] No agent - returning")
            return

        context = self.agent.context
        if not hasattr(context, "agent0"):
            print("[HINDSIGHT RETAIN] No agent0 on context - returning")
            return
        # Check if hindsight_client is available before proceeding
        if not hindsight_helper.is_hindsight_client_available():
            print("[HINDSIGHT RETAIN] hindsight_client not available - returning")
            return

        if not hindsight_helper.is_configured(context):
            print("[HINDSIGHT RETAIN] Not configured - returning")
            return

        config = hindsight_helper._get_plugin_config(self.agent)
        print(f"[HINDSIGHT RETAIN] Config resolved: base_url={config.get('hindsight_base_url','?')}, retain_enabled={config.get('hindsight_retain_enabled')}")
        if not config.get("hindsight_retain_enabled", True):
            print("[HINDSIGHT RETAIN] Retain disabled in config - returning")
            return

        # Run retention in background to avoid blocking
        # Create DeferredTask and start the async background task
        task = DeferredTask()
        task.start_task(
            self._retain_to_hindsight,
            self.agent,
            context,
            loop_data,
            config,
        )

    @staticmethod
    async def _retain_to_hindsight(agent, context, loop_data, config):
        """Background task: extract knowledge and store in Hindsight."""
        try:
            log_item = context.log.log(
                type="util",
                heading="Retaining to Hindsight...",
            )

            # Get the conversation history to extract what should be retained
            system = agent.read_prompt("hindsight.retain_extract.sys.md")
            msgs_text = agent.concat_messages(agent.history)

            # Call utility LLM to extract key information from conversation
            memories_json = await agent.call_utility_model(
                system=system,
                message=msgs_text,
                background=True,
            )

            if not memories_json or not isinstance(memories_json, str):
                log_item.update(heading="No content to retain to Hindsight.")
                return

            memories_json = memories_json.strip()
            if not memories_json:
                log_item.update(heading="Empty response for Hindsight retain.")
                return

            try:
                memories = DirtyJson.parse_string(memories_json)
            except Exception as e:
                log_item.update(heading=f"Failed to parse retain content: {e}")
                return

            if memories is None:
                log_item.update(heading="No valid content to retain.")
                return

            if not isinstance(memories, list):
                if isinstance(memories, (str, dict)):
                    memories = [memories]
                else:
                    log_item.update(heading="Invalid retain content format.")
                    return

            if len(memories) == 0:
                log_item.update(heading="No useful information to retain to Hindsight.")
                return

            # Retain each memory to Hindsight
            retained = 0
            failed = 0
            for memory in memories:
                content = str(memory).strip()
                if not content:
                    continue

                success = await hindsight_helper.retain_memory(
                    context=context,
                    content=content,
                )
                if success:
                    retained += 1
                else:
                    failed += 1

            bank_id = hindsight_helper.get_bank_id(context)
            log_item.update(
                heading=f"Hindsight: {retained} memories retained to bank '{bank_id}'",
                content=f"Retained: {retained}, Failed: {failed}",
            )

        except Exception as e:
            try:
                err = errors.format_error(e)
                context.log.log(
                    type="warning",
                    heading="Hindsight retain background error",
                    content=err,
                )
            except Exception:
                pass
