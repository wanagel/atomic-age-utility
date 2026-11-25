# Atomic Age Utility

A native Home Assistant theme for household wall tablets, styled after 1950s enamel appliances and analog instruments. Day Console uses ivory, deep teal and offset shadows. Night Console uses charcoal instrument surfaces and warm lettering. Home Assistant’s Light, Dark and Auto options control the mode.

The theme targets Home Assistant Core 2026.11.2 and later. The local Dashboard Lab is pinned to 2026.11.3. See [QA results](docs/qa.md) for the test coverage and open checks.

## Install the theme

1. Confirm that the existing `frontend` configuration includes the themes directory. Add the following under the existing `frontend` mapping if needed, then check configuration and restart once.

   ```yaml
   frontend:
     themes: !include_dir_merge_named themes
   ```

2. Copy [atomic-age-utility.yaml](themes/atomic-age-utility.yaml) into `<config>/themes/`.
3. In **Tools → Actions**, run `frontend.reload_themes`.
4. In **Profile → Theme**, select **Atomic Age Utility**. Set **Light** for Day Console, **Dark** for Night Console, or **Auto** to follow the client. Use a view’s `theme` setting to scope theming to its cards and canvas. Profile selection also themes the sidebar and other Home Assistant screens.

The repository has Marketplace metadata. After publication to a public GitHub repository, remove the manually copied YAML, reload themes, and add the repository URL in **Settings → Marketplace → Add from link**. Choose **Theme** if asked, install, and select the theme from the profile. Marketplace publication and install are pending.

For manual updates, replace the YAML and reload themes. To remove a manual installation, switch the profile and any themed views back to the default, remove the copied YAML, and reload. For a Marketplace installation, switch selectors first and then uninstall through Marketplace.

## Kitchen Lab dashboard

The local lab dashboard is at [Atomic Age Utility](http://127.0.0.1:8123/atomic-age-utility/home). It includes Kitchen, Lighting, Climate, Security, Cameras, and Maintenance. Bright and All Off operate the lab light helper. House Conditions displays explicitly labeled lab fixtures. Security’s simulation uses the lab alert helper and Maintenance clears it.

To reproduce it, create a new dashboard from scratch in **Settings → Dashboards** with URL path `atomic-age-utility`. Open **Edit dashboard → menu → Raw configuration editor**, paste the contents of [kitchen-lab.json](examples/kitchen-lab.json), and save. The raw editor accepts this JSON as YAML and saves it through Home Assistant’s storage dashboard API. The new dashboard uses the existing lab light and alert booleans and the lab temperature input number.

## Reuse the room patterns

[Room profiles](examples/rooms/) cover Kitchen, Sara’s Office, Living Room, Family Room, Master Bedroom, and Studio. The profiles include IDs explicitly supplied by the design spec and empty fields for devices that require household discovery. Sara’s Office, in particular, is designed around direct lighting and media controls until named scenes exist.

1. Check the household’s entity inventory and features, then create a local JSON array of verified entity IDs. Keep that inventory out of the repository.
2. Fill the relevant room profile. Put the room’s frequently used tiles under `controls` and individual devices under `lights`, `covers`, and `media`. Each entry takes `entity`, `label`, and `icon`, plus optional native tile `features` such as `light-brightness` or `cover-position` when supported. Add only existing scenes under `programs`. Temperature and climate are separate fields. Use a Fahrenheit temperature source with the current dial scale of 45–95 °F or adjust that scale for your source before generating.
3. Generate the dashboard using the same hyphenated slug that will be entered when you create the storage dashboard.

   ```sh
   python3 examples/build_dashboard.py \
     --slug atomic-kitchen \
     --profile examples/rooms/kitchen.json \
     --inventory /path/to/verified-entity-ids.json > kitchen.json
   ```

4. Save the generated configuration through the raw editor of the newly created storage dashboard. The generator includes controls and scenes only when their IDs are in the supplied inventory. Review the generated actions and confirm what each whole-room scene does before enabling it for the household.
5. Create one dashboard per tablet as needed. Set the bedroom or media tablet’s lab or household profile to Dark if it should always use Night Console. Home Assistant’s Auto preference lets the client choose its mode.

The home view leads with programs and room controls, then House Conditions. Detail links appear when the corresponding room controls exist. Cameras appear in a separate subview when verified feeds are mapped. Security summaries are read-only. Maintenance consolidates offline room devices behind one home-view advisory. A hidden subview is a navigation choice and inherits the dashboard’s access rules.

## Dependencies and visual choices

The theme and dashboard use built-in Home Assistant variables, native Sections, Material Design Icons, and the native gauge for the comfort dial. There are no custom resources, fonts, or card-mod rules to install. The header uses native text with a monospace product line. The theme uses deeper foreground shades of teal, gold, and coral where contrast requires it, while preserving the swatches defined in the design specification.

Native theme behavior and card options are documented in the [theme authoring guide](https://contributors.home-assistant.io/marketplace/guides/themes/), [Sections guide](https://www.home-assistant.io/dashboards/sections/), and [Shortcut card reference](https://www.home-assistant.io/dashboards/shortcut/).
