#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
import json
import os
import sys
import subprocess


def get_event_message(event_type, event_details=None):
    """Return appropriate message for the event type with details if available."""
    if event_type == "stop":
        if event_details and event_details.get("duration"):
            return f"Claude task completed in {event_details['duration']}"
        return "Claude task completed!"
    
    elif event_type == "subagent_stop":
        if event_details and event_details.get("agent_type"):
            return f"{event_details['agent_type']} subagent finished!"
        return "Subagent task completed!"
    
    elif event_type == "pre_tool_use":
        if event_details and event_details.get("tool_name"):
            return f"About to use {event_details['tool_name']}"
        return "Preparing to use a tool"
    
    elif event_type == "error":
        if event_details and event_details.get("error_type"):
            return f"Error: {event_details['error_type']}"
        return "Claude encountered an issue"
    
    else:  # default
        return "Claude notification"


def parse_event_details(details_str):
    """Parse event details from JSON string or environment variables."""
    details = {}
    
    # Try to parse JSON details if provided
    if details_str:
        try:
            details = json.loads(details_str)
        except json.JSONDecodeError:
            # If not JSON, treat as simple key=value pairs
            for pair in details_str.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    details[key.strip()] = value.strip()
    
    # Check environment variables for common hook details
    if os.getenv("CLAUDE_TOOL_NAME"):
        details["tool_name"] = os.getenv("CLAUDE_TOOL_NAME")
    
    if os.getenv("CLAUDE_AGENT_TYPE"):
        details["agent_type"] = os.getenv("CLAUDE_AGENT_TYPE")
    
    if os.getenv("CLAUDE_ERROR_TYPE"):
        details["error_type"] = os.getenv("CLAUDE_ERROR_TYPE")
    
    if os.getenv("CLAUDE_DURATION"):
        details["duration"] = os.getenv("CLAUDE_DURATION")
    
    return details


def send_macos_notification(title, message, subtitle=None, sound="Glass"):
    """Send a native macOS notification using osascript."""
    try:
        # Build the AppleScript command
        script_parts = [f'display notification "{message}" with title "{title}"']
        
        if subtitle:
            script_parts[0] += f' subtitle "{subtitle}"'
        
        if sound:
            script_parts[0] += f' sound name "{sound}"'

        # Execute the notification
        subprocess.run(
            ["osascript", "-e", script_parts[0]],
            capture_output=True,
            timeout=5,
        )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Fail silently if notification system encounters issues
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Send macOS notifications for Claude events")
        parser.add_argument("--event", "-e", choices=["stop", "subagent_stop", "pre_tool_use", "error"], 
                           default="default", help="Type of Claude event")
        parser.add_argument("--message", "-m", help="Custom message to display")
        parser.add_argument("--details", "-d", help="Event details as JSON or key=value pairs")
        parser.add_argument("--title", "-t", default="Claude Code", help="Notification title")
        parser.add_argument("--subtitle", "-s", help="Notification subtitle")
        parser.add_argument("--sound", default="Glass", help="Notification sound")
        
        args = parser.parse_args()
        
        # Use custom message if provided, otherwise generate based on event and details
        if args.message:
            message = args.message
        else:
            event_details = parse_event_details(args.details)
            message = get_event_message(args.event, event_details)
        
        # Send the notification
        send_macos_notification(
            title=args.title,
            message=message,
            subtitle=args.subtitle,
            sound=args.sound
        )

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()