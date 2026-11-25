"""Build a native Sections dashboard for Home Assistant's storage editor."""
import argparse
import json
from pathlib import Path

THEME = "Atomic Age Utility"
LAB_LIGHT = "input_boolean.lab_light"
LAB_ALERT = "input_boolean.lab_alert"
LAB_TEMP = "input_number.lab_temperature"
MISSING = ["unknown", "unavailable"]


def go(slug, path):
    return {"action": "navigate", "navigation_path": f"/{slug}/{path}"}


def heading(label, icon):
    return {"type": "heading", "heading": label, "heading_style": "title", "icon": icon}


def section(label, icon, *cards):
    return {"type": "grid", "cards": [heading(label, icon), *cards]}


def shortcut(label, icon, action, columns="full"):
    return {
        "type": "shortcut", "label": label, "icon": icon, "tap_action": action,
        "grid_options": {"columns": columns, "rows": 1},
    }


def action(service, entity):
    return {
        "action": "perform-action", "perform_action": service,
        "target": {"entity_id": entity},
    }


def tile(entity, label, icon, tap=None, features=()):
    result = {
        "type": "tile", "entity": entity, "name": label, "icon": icon,
        "tap_action": tap or {"action": "more-info"},
        "icon_tap_action": tap or {"action": "more-info"},
        "grid_options": {"columns": "full"},
    }
    if features:
        result["features"] = [{"type": feature} for feature in features]
    return result


def when(entity, states):
    return {"condition": "state", "entity": entity, "state": states}


def conditional(card, *conditions):
    return {"type": "conditional", "conditions": list(conditions), "card": card}


def markdown(content):
    return {"type": "markdown", "content": content, "grid_options": {"columns": "full", "rows": "auto"}}


def view(slug, title, path, *sections):
    result = {
        "title": title, "path": path, "type": "sections", "theme": THEME,
        "max_columns": 3, "dense_section_placement": False, "sections": list(sections),
    }
    if path != "home":
        result.update(subview=True, back_path=f"/{slug}/home")
    return result


def badge(entity, label, icon, tap):
    return {
        "type": "entity", "entity": entity, "name": label, "icon": icon,
        "show_name": True, "show_state": True, "show_icon": True, "tap_action": tap,
    }


def gauge(entity, label):
    return {
        "type": "gauge", "entity": entity, "name": label, "needle": True,
        "min": 45, "max": 95, "grid_options": {"columns": "full", "rows": 3},
    }


def history(entity):
    return {
        "type": "history-graph", "entities": [entity], "hours_to_show": 6,
        "grid_options": {"columns": "full", "rows": 4},
    }


def lab_dashboard(slug):
    toggle = {"action": "toggle"}
    alert = """{% if is_state('input_boolean.lab_alert', 'on') %}
- **Home alarm** · Pending
- **Doors** · Open
{% else %}
- **Home alarm** · Disarmed
- **Doors** · Closed
{% endif %}
- **Windows** · Closed
- **Glass break** · Clear
- **Cameras** · No lab feed"""
    annunciator = markdown(alert)
    advisory = conditional(
        shortcut("1 lab advisory", "mdi:alert-outline", go(slug, "maintenance")),
        when(LAB_ALERT, "on"),
    )
    confirm = action("input_boolean.turn_on", LAB_ALERT)
    confirm["confirmation"] = {"text": "Simulate an alarm advisory in the Dashboard Lab?"}
    home = view(
        slug, "Kitchen", "home",
        section("Automatic Programs", "mdi:tune-variant",
                shortcut("Bright", "mdi:white-balance-sunny", action("input_boolean.turn_on", LAB_LIGHT), 6),
                shortcut("All Off", "mdi:power", action("input_boolean.turn_off", LAB_LIGHT), 6),
                shortcut("Assist", "mdi:message-processing-outline", {"action": "assist"}),
                gauge(LAB_TEMP, "Kitchen temperature")),
        section("Room Controls", "mdi:knob",
                tile(LAB_LIGHT, "All kitchen lights", "mdi:lightbulb", toggle),
                shortcut("Lighting circuits", "mdi:lightbulb-group-outline", go(slug, "lights")),
                shortcut("Climate", "mdi:thermometer", go(slug, "climate"))),
        section("House Conditions", "mdi:shield-home-outline", annunciator, advisory,
                shortcut("Security", "mdi:shield-home", go(slug, "security"))),
    )
    home["header"] = {
        "layout": "start", "badges_position": "bottom",
        "card": {"type": "markdown", "text_only": True,
                 "content": "# Kitchen\n\n`DOMESTIC CONTROL STATION` · Dashboard Lab"},
    }
    home["badges"] = [
        badge(LAB_TEMP, "Room temperature", "mdi:thermometer", go(slug, "climate")),
    ]
    return {"views": [
        home,
        view(slug, "Lighting", "lights", section("Lighting Circuits", "mdi:lightbulb-group",
             tile(LAB_LIGHT, "All kitchen lights", "mdi:lightbulb", toggle))),
        view(slug, "Climate", "climate",
             section("Comfort Dial", "mdi:thermometer", gauge(LAB_TEMP, "Kitchen temperature"),
                     tile(LAB_TEMP, "Lab temperature", "mdi:thermometer")),
             section("Temperature History", "mdi:chart-line", history(LAB_TEMP))),
        view(slug, "Security", "security", section("House Conditions", "mdi:shield-home",
             annunciator, shortcut("Cameras", "mdi:cctv", go(slug, "cameras")),
             shortcut("Simulate advisory", "mdi:alert-outline", confirm))),
        view(slug, "Cameras", "cameras", section("Cameras", "mdi:cctv",
             markdown("Dashboard Lab has no camera feeds."))),
        view(slug, "Maintenance", "maintenance", section("Local Advisories", "mdi:wrench",
             conditional(markdown("**Lab advisory** · Simulated door status is open."), when(LAB_ALERT, "on")),
             conditional(markdown("No active advisories."), when(LAB_ALERT, "off")),
             shortcut("Clear lab advisory", "mdi:check", action("input_boolean.turn_off", LAB_ALERT)))),
    ]}


def room_dashboard(slug, profile, inventory):
    def available_id(key):
        entity = profile.get(key)
        return entity if entity in inventory else None

    def control(entity, label, icon, features=()):
        tap = {"action": "toggle"} if entity.startswith(("light.", "switch.")) else None
        return tile(entity, label, icon, tap, features)

    def group_cards(key):
        return [
            control(entry["entity"], entry["label"], entry["icon"], entry.get("features", []))
            for entry in profile.get(key, []) if entry["entity"] in inventory
        ]

    programs = []
    for entry in profile.get("programs", []):
        entity = entry["entity"]
        if entity in inventory:
            card = shortcut(entry["label"], entry["icon"], action("scene.turn_on", entity), 6)
            programs.append(conditional(card, {"condition": "state", "entity": entity,
                                                "state_not": MISSING}))
    if profile.get("assist"):
        programs.append(shortcut("Assist", "mdi:message-processing-outline", {"action": "assist"}))

    controls = group_cards("controls")
    lights, covers, media = (group_cards(key) for key in ("lights", "covers", "media"))
    temperature, climate = available_id("temperature"), available_id("climate")
    cameras = [entry for entry in profile.get("cameras", []) if entry["entity"] in inventory]
    climate_card = control(climate, "Climate", "mdi:hvac", ["target-temperature"]) if climate else None
    detail = []
    for title, path, icon, cards in (
        ("Lighting", "lights", "mdi:lightbulb-group", lights),
        ("Shades", "shades", "mdi:blinds-horizontal", covers),
        ("Climate", "climate", "mdi:thermometer",
         [*([gauge(temperature, "Room temperature"), history(temperature)] if temperature else []),
          *([climate_card] if climate_card else [])]),
        ("Media", "media", "mdi:television", media),
    ):
        if cards:
            controls.append(shortcut(title, icon, go(slug, path)))
            detail.append(view(slug, title, path, section(title, icon, *cards)))

    indicators = [
        ("Home alarm", "mdi:shield-home", "alarm", {"disarmed": "Disarmed", "armed_home": "Armed home",
         "armed_away": "Armed away", "armed_night": "Armed night", "armed_vacation": "Armed vacation",
         "armed_custom_bypass": "Armed with bypass", "arming": "Arming", "pending": "Pending",
         "triggered": "Triggered", "disarming": "Disarming"}),
        ("Doors", "mdi:door-closed", "doors", {"on": "Open", "off": "Closed"}),
        ("Windows", "mdi:window-closed", "windows", {"on": "Open", "off": "Closed"}),
        ("Glass break", "mdi:shield-check-outline", "glass_break", {"on": "Detected", "off": "Clear"}),
    ]
    status_lines = []
    badges = []
    for label, icon, key, mapping in indicators:
        entity = available_id(key)
        state = f"{{{{ {mapping!r}.get(states('{entity}'), 'Unavailable') }}}}" if entity else "Unavailable"
        status_lines.append(f"- **{label}** · {state}")
        if entity and key in {"alarm", "doors", "windows"}:
            badges.append(badge(entity, label, icon, go(slug, "security")))
    if cameras:
        camera_ids = [entry["entity"] for entry in cameras]
        status_lines.append(f"- **Cameras** · {{{{ expand({camera_ids!r}) | rejectattr('state', 'in', {MISSING!r}) | list | length }}}} available")
    else:
        status_lines.append("- **Cameras** · Unavailable")

    advisory_entries = {
        card["entity"]: card["name"] for card in [*group_cards("controls"), *lights, *covers, *media]
    }
    for entry in profile.get("advisories", []):
        if entry["entity"] in inventory:
            advisory_entries[entry["entity"]] = entry["label"]
    if climate:
        advisory_entries[climate] = "Climate"
    if temperature:
        advisory_entries[temperature] = "Room temperature"
    status = markdown("\n".join(status_lines))
    advisory_cards = []
    if advisory_entries:
        conditions = [{"condition": "or", "conditions": [
            when(entity, MISSING) for entity in advisory_entries
        ]}]
        advisory_cards.append(conditional(
            shortcut("Room advisory", "mdi:alert-outline", go(slug, "maintenance")), *conditions))
    maintenance = [
        conditional(markdown(f"**{label}** · Unavailable"), when(entity, MISSING))
        for entity, label in advisory_entries.items()
    ]
    if advisory_entries:
        maintenance.append(conditional(markdown("No active advisories."), *[
            {"condition": "state", "entity": entity, "state_not": MISSING}
            for entity in advisory_entries
        ]))
    else:
        maintenance.append(markdown("No room devices configured for advisories."))

    room_sections = []
    if programs:
        if temperature:
            programs.append(gauge(temperature, "Room temperature"))
        room_sections.append(section("Automatic Programs", "mdi:tune-variant", *programs))
    elif temperature:
        controls = [gauge(temperature, "Room temperature"), *controls]
    if controls:
        room_sections.append(section("Room Controls", "mdi:knob", *controls))
    room_sections.append(section("House Conditions", "mdi:shield-home-outline", status,
                         *advisory_cards, shortcut("Security", "mdi:shield-home", go(slug, "security"))))
    home = view(slug, profile["title"], "home", *room_sections)
    home["header"] = {
        "layout": "start", "badges_position": "bottom",
        "card": {"type": "markdown", "text_only": True,
                 "content": f"# {profile['title']}\n\n`DOMESTIC CONTROL STATION`"},
    }
    if temperature:
        badges.insert(0, badge(temperature, "Room temperature", "mdi:thermometer", go(slug, "climate")))
    home["badges"] = badges
    security_cards = [status]
    if cameras:
        security_cards.append(shortcut("Cameras", "mdi:cctv", go(slug, "cameras")))
        detail.append(view(slug, "Cameras", "cameras", section("Cameras", "mdi:cctv", *[
            {"type": "picture-entity", "entity": entry["entity"], "name": entry["label"],
             "show_state": False, "camera_view": "auto", "tap_action": {"action": "more-info"}}
            for entry in cameras
        ])))
    return {"views": [home, *detail,
        view(slug, "Security", "security", section("House Conditions", "mdi:shield-home", *security_cards)),
        view(slug, "Maintenance", "maintenance", section("Local Advisories", "mdi:wrench", *maintenance)),
    ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", action="store_true", help="Build for the isolated Dashboard Lab fixtures.")
    parser.add_argument("--profile", type=Path, help="Room profile JSON.")
    parser.add_argument("--inventory", type=Path, help="JSON array of verified Home Assistant entity IDs.")
    parser.add_argument("--slug", default="atomic-age-utility", help="Storage dashboard URL path.")
    args = parser.parse_args()
    if "-" not in args.slug or not all(c.isascii() and (c.islower() or c.isdigit() or c == "-") for c in args.slug):
        parser.error("Use a lowercase hyphenated dashboard URL path.")
    if args.lab and not (args.profile or args.inventory):
        dashboard = lab_dashboard(args.slug)
    elif not args.lab and args.profile and args.inventory:
        profile = json.loads(args.profile.read_text())
        inventory = set(json.loads(args.inventory.read_text()))
        dashboard = room_dashboard(args.slug, profile, inventory)
    else:
        parser.error("Supply either --lab or both --profile and --inventory.")
    print(json.dumps(dashboard, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
