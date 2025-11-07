#!/usr/bin/env python3
"""
Helper script to get Telegram chat information
Usage: python scripts/get_telegram_info.py <bot_token>
"""

import sys
import httpx


def get_updates(bot_token: str):
    """Fetch recent updates from Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                print(f"Error: {data.get('description', 'Unknown error')}")
                return

            updates = data.get("result", [])

            if not updates:
                print("No updates found. Please send a message to your bot first.")
                return

            print("\n" + "=" * 60)
            print("TELEGRAM CHAT INFORMATION")
            print("=" * 60 + "\n")

            for update in updates[-5:]:  # Show last 5 updates
                message = update.get("message", {})
                chat = message.get("chat", {})

                if chat:
                    print(f"Chat ID: {chat.get('id')}")
                    print(f"Chat Type: {chat.get('type')}")
                    print(f"Chat Title: {chat.get('title', 'N/A')}")

                    if "message_thread_id" in message:
                        print(f"Thread ID: {message.get('message_thread_id')}")

                    print(f"Message: {message.get('text', 'N/A')[:50]}")
                    print("-" * 60)

            print("\nUse these values in your .env file:")
            last_chat = updates[-1].get("message", {}).get("chat", {})
            print(f"TELEGRAM_CHAT_ID={last_chat.get('id')}")

            last_thread = updates[-1].get("message", {}).get("message_thread_id")
            if last_thread:
                print(f"TELEGRAM_THREAD_ID={last_thread}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/get_telegram_info.py <bot_token>")
        sys.exit(1)

    bot_token = sys.argv[1]
    get_updates(bot_token)
