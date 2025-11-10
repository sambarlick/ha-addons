# Fing Agent Home Assistant Add-on

Runs the official `fing/fing-agent` Docker container as a Home Assistant add-on.

This agent allows your Home Assistant instance to be discovered by the Fing mobile app and enables the official Fing integration in Home Assistant.

## How to Use

1.  **Start the Add-on:** Make sure the add-on is started and running.
2.  **Open Fing App:** Open the Fing mobile app on your phone (while connected to the same network).
3.  **Link Agent:** The app should automatically discover a new, unlinked agent. Follow the prompts in the app to link this agent to your Fing account.
4.  **Add HA Integration:** Once linked, go to **Settings > Devices & Services** in Home Assistant, click **Add Integration**, and search for **Fing**. It will connect to this local agent.

## Configuration

This add-on requires no configuration.

---

## Attribution

This add-on is a wrapper for the official Docker image provided by **Fing**. All credit for the Fing Agent software, it's functionality, and the "Fing" name and brand belong to Fing (fing.com).

This add-on simply makes it possible to run their official agent on Home Assistant OS.
