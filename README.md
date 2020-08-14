# twardoch-fontlab-scripts

- Python scripts for [FontLab 7](http://fontlab.info)
- by Adam Twardoch
- Licensed at your choice under:
  - [CC-0](./LICENSE) (public domain)
  - MIT license, Copyright © 2020 Adam Twardoch

## Installation

### <a class="github-button" href="https://github.com/twardoch/twardoch-fontlab-scripts/archive/master.zip" data-color-scheme="no-preference: dark; light: dark; dark: dark;" data-icon="octicon-download" data-size="large" aria-label="Download github.com/twardoch/twardoch-fontlab-scripts/archive/master.zip">Download ZIP</a>

<button><a class="btn btn-primary" href="https://github.com/twardoch/twardoch-fontlab-scripts/archive/master.zip">Download ZIP</a></button>

1. Unzip the downloaded file.
2. With Finder or File Explorer, go inside the `Script` subfolder that is inside the unzipped folder.
3. Run FontLab 7, choose _Scripts > Update / Install Scripts_. This will install [TypeRig](https://github.com/kateliev/TypeRig), an extension library for FontLab 7 that is needed for some of the scripts. Restart FontLab after the installation completes. 
4. In FontLab 7, from the _FontLab 7_ menu (Mac) or _Edit_ menu (Windows), choose _Preferences > General_, and click the _Open user data folder_ button (on the right of _User data_. This will open a Finder or File Explorer window, with your [user data folder](https://help.fontlab.com/fontlab/7/manual/Custom-data-files-and-locations/#user-data-folder) named `FontLab 7`. 
5. If there is no `Scripts` folder inside the `FontLab 7` user data folder, create it.
6. Copy the contents of the unzipped `Scripts` folder into the `Scripts` folder in your user data folder.
7. Run FontLab 7, or if it’s running, choose _Scripts > Refresh Scripts_

**Note:** This is not an official Fontlab Ltd. product. No technical support, no warranty whatsoever — but pull requests are welcome.

## Usage

Open a font and run the scripts from the _Scripts_ menu.

### TW Export Fonts > Export Fonts in Folder

![](./docs/img/Export_Fonts_in_Folder.png)

1. In FontLab 7, choose **Scripts > TW Export Fonts > Export Fonts in Folder**
2. Choose the **Source folder** where you have your source `.vfc`, `.vfj`, `.vfb`, `.otf`, `.ttf` etc. (defaults to folder in which the currently open font is saved).
3. Specify which font types you’d like to convert, and whether the script should also recursively search in the subfolders of the Source folder.
4. Choose the **Destination folder** in which the exported fonts will be written.
5. Click **Export Fonts As**, choose (and customize if needed) the export **Profile** (format and settings), and choose **Content** that you want to export (Current layer, Instances or Masters). _Don’t change the Destination settings, they’re special._ Click **Export**.
6. The script looks for all the source fonts, opens each one and exports with your settings.
   - If you turned on Subfolders, it’ll replicate the subfolder structure in the Destination folder.
   - If a font is exported as one file (e.g. OpenType PS .otf with Current layer setting), the base filename of the source file will be used as the name of the exported file.
   - If a font is exported as multiple fonts file (Masters, Instances, color fonts or web fonts), the base filename of the source file will be used as the name of a subfolder, and the exported files will be written inside that subfolder.

### TW Glyph Names and Unicode > Generate Unicodes by NAM

![](./docs/img/Generate_Unicodes_by_NAM.png)

1. In FontLab 7, open a font and choose **Scripts > TW Glyph Names and Unicode > Generate Unicodes by NAM**
2. Choose a Unicode-to-glyphname [NAM mapping file](https://help.fontlab.com/fontlab/7/manual/Custom-data-files-and-locations/#glyph-name-to-unicode-mapping-rules-standardnam) (with `.nam` file extension) that contains your custom Unicode-to-glyphname assignments (for example, “double-encoding”)
3. Choose whether the script should flag (color-mark) the glyphs in which it changed Unicode codepoints, and whether it should keep Unicodes for glyphs not covered by the NAM (otherwise it’ll unencode those glyphs)
4. Click **Generate Unicodes** to re-generate Unicodes in all glyphs in the font based on the NAM file.

As a separate functionality, you can also open a font, run the script and click **Save NAM file**. This will contain the Unicode-to-glyphname mapping of the current font.

### TW Anchors > Select Glyphs by Anchor

![](./docs/img/Select_Glyphs_by_Anchor.png)

While in Font window, run the script (if your font is large, it may take a while for the dialog to show up). The combo box shows all anchors found in all glyphs in all masters — pick one or type your own. Choose whether to search for a given anchor in the current master or all masters with the checkbox. Click Search, and all glyphs that include the anchor will be selected, plus their names will be printed to the Output panel, `/`-separated.

Requires TypeRig.

<!-- Place this tag in your head or just before your close body tag. -->
<script async defer src="https://buttons.github.io/buttons.js"></script>
