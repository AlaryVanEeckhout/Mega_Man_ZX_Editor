# Running the Application

First you need to make sure the dependencies are installed. See [the "Setup for usage" section in README.md](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/README.md#setup-for-usage) for more information.  
To run the application, the file named "MME_NDS.py" must be run using python 3.

> [!TIP]
> If you want to quickly know what an element of the UI is or does, there are usually two ways to find out. You can hover your mouse over the element and a tooltip will likely appear. Otherwise, you may see a description appear in the status bar, at the bottom left of the application window.

# Opening a ROM

Once the application is running, there are two ways to open a ROM.
1. In the File menu, click on the "Open" option with a folder icon
2. In the toolbar, click on the folder icon.

In both cases, a dialog will pop-up, prompting you to open the desired ROM file.  
The dialog will only show files with the ".nds" or ".srl" extension, so if your ROM is in a zip file, you will have to extract it first.

Select the file, and click on the "Open" button.  
A progress bar will appear with the game's icon and title.

Once this progress bar disappears, the internal filesystem of the ROM will be displayed in a list on the left panel in the "File Explorer" tab.  
This means the ROM opened successfully.

> [!WARNING]
> If you try to open a ROM that is not supported by the editor, some features of the editor may not work as intended or the ROM may fail to open at all.

# Opening a File in the ROM

To open a file, simply click on it from the list of files.

By default, the application will try to guess what the file is and display its contents on the right panel accordingly.

On the top left of that panel, there is a "Save changes" button. This is for saving the changes you made in the right panel only.  


> [!NOTE]
> If the application does not know what to do with the file, it will show a message indicating so.  
> If you know what this file is supposed to be, you can always set the view state from the "View" menu

## Dialogue Files

Dialogues are separated into what the application refers to as "messages".  
Each of those messages are usually separated by in-game events such as characters moving during a cutscene.

The right panel contains the text of the current message you are viewing.  
Above the text area, there is a dropdown allowing you to choose what message index to go to.
A check box labeled "Overwrite existing text" is also present to the left of the dropdown. It toggles [overtype mode](https://en.wikipedia.org/wiki/Insert_key).

> [!TIP]
> You can right-click on the text area to open a list of special commands that can be inserted in the dialogue  
> For more information on special commands, see [the wiki section on it](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/wiki/Mega-Man-ZX-(USA)-Dialogue-chars-table)

## Graphic Files
Graphics are generally structured with a header with pointers to all the relevant data, the graphics data and the palettes.  
Each of those structures are referred to as "images", whereas a set of images is called an "entry", since it is pointed to by the pointer table at the start of the file.

Over the canvas, there are two dropdowns next to one another: the one on the left for entries and the other for images.

To the left of the entry dropdown, the current palette is represented by 256 buttons. Upon loading an image, the application will attempt to load the correct palette.

If it succeeds, the dropdown under the entry and image dropdowns will be empty.  
Otherwise, you will see "Default Palette", or the name of the last preset palette you selected.

## Font Files

Font files are somewhat similar to graphic files, but they have 1bpp graphics with a black-and-white palette, and the header is different in structure.

The spinbox labeled "char width" controls the width in pixels of each character, but there is a restriction: the width must be even, otherwise the game will crash.
The spinbox labeled "char height" changes the height in pixels of each character.

> [!NOTE]
> The application currently only shows tile widths divisible by eight, since this works to render the fonts in ZX and ZXA. However, having another width value has a peculiar effect.

## OAM Files

OAM stands for Object Attribute Memory.  
Each OAM file relies on a graphic file for rendering.  
The OAM file is called \<name\>_dat.bin and the associated graphic file is called \<name\>_fnt.bin.

The dropdown at the top allows you to select the "entry" to load, which corresponds exactly with the entry of the same index in the associated graphic file.

The OAM Editor has two tabs: Frames and Animations.

### Frames

Frames are composed of objects, which refer to graphics and have some attributes.

The dropdown on the top left of the tab is for selecting the frame to view.  
The dropdown to the right is for selecting the object to edit.  
Under that dropdown is a button that, for convienience, makes a selection box appear over the current object.

The "Add object" button inserts an object right after the current one in the list, and selects that object.  
The "Remove object" button removes the object from the list.

The spinbox under the "frame" dropdown controls the tile ID where this objects'graphics should be loaded from. It is not the same as the VRAM tile ID, as its indexes have half the resolution.  
The checkboxes labeled "Filp H" and "Filp V" allow to filp the object horizontally and vertically, respectively.  
The slider controls the dimensions of the current object and its graphics.  
The "Shape" options allow to get different dimension options for the slider.
The two spinboxes below are, from left to right, for the X and Y position of the object. Those positions are in a value range from -0x80 to 0x7F.

### Animations

In this tab, the canvas is just there to visualise animations, and does not allow frame modifications.  
Animations are a set of frame indexes and durations.  
The duration value works in a peculiar way:
- At the first frame of the animation, it is simply a 0x00-0xFF duration value in frames.
- After the first frame, 0xFF is used to end the animation, 0xFE is used to begin a loop (causing the frame index to be used as a looping point parameter), and 0x00 becomes a duration of 0xFF frames.

The dropdown at the top left allows to select the current animation.  
The dropdown to the right lets you select a frame of the animation to view and edit.

Normal frames can be adjusted via the two spinboxes under the "frame" dropdown.  
The first one is for changing the frame index, and the second one is for changing the duration value.

The last frame is represented by the checkbox labeled "loop" and the spinbox below it for the loop index.

The "Add Frame" button inserts a new animation frame directly after the currently selected frame in the dropdown, and selects that frame automatically.

The "Remove Frame" button removes the currently selected animation frame from the list.

> [!WARNING]
> The saving of animations with removed or added frames is not yet on point, so avoid changing the amount of frames an animation has for now

Just above the canvas, there are three media playback buttons.  
The play button in the middle will play the currently selected animation from the currently selected frame.

Once the end of the animation is reached, you can click the button on the left to go back to the first frame.

## Model Files

The first dropdown allows you to select the model entry to view.  
The second dropdown allows you to select the model to view.

### Camera Controls
Rotation around the model: WASD  
Zoom in/out: E/Q, respectively  
Preview initial view: R


## SDAT Files

A game may contain more than one SDAT.  
There are two ways to open an SDAT file:  
1. Right-click on the file in the list, and click on "Open Sound Archive".
2. In the toolbar, click on the megaphone icon.

From there, a new window titled "Sound Data Archive" will open.  
In this window, a dropdown allows you to choose an SDAT to view from the list of SDATs.

### Playback

The toolbar contains a Play/Pause button, a Stop button, and a Plot button.

### SSEQ Modification

For SSEQs or SSARs, if you expand them, you will see a list of events.  
Double-clicking or pressing Enter on those events will open an input dialog.

## VX Files
Those files use the Actimagine video codec to encode videos and sound effects.

The right panel only allows you to see the file's header.  
To properly see the contents of this kind of file, you need to export it.

# Exporting a File

There are two ways to export a file:
1. Right-click on the file in the list, and click on "Export \<name\>".
2. Once the file is open, go in the File menu and click on "Export..."

A dialog will pop-up, prompting you to choose the location to save.

Then, another dialog will pop-up to choose how to save the file.

The first dropdown allows you to choose the format.

The two other dropdowns allow you to choose the compression operation to perform on the file before exporting.  
The dropdown on the left allows you to leave the file as-is (default), compress it, or decompress it.  
The dropdown on the right allows you to select what algorithm to use (if applicable).  
If unsure, you should leave those dropdowns at their default values.

# Importing a File

# Editing a Level

On the right panel, there is the level canvas, the place where the full level will be rendered once loaded.  
On the left panel, there are three tabs: Tileset, Screens, and Entities.

## Tileset

The graphics, collision, and screen definitions are stored in regular binary files rather than the ARM9 overlays.

The canvas shows on the left a grayscale image of the graphics used and on the right a full list of all available tiles.  
To draw tiles in a screen, simply click on that tile from the tileset canvas and click on the tile you want to replace in the level canvas.

## Screens

The screen layout data is stored in the level overlay.

This is where you can change the screen arrangement of the level.  
Levels have multiple layers with a unique layout each.

Each layout has its own tab: Layout 0, Layout 1, Layout 2, Layout 3, Camera Scroll Layout, Radar Scope Layout, Tileset Offset Map, and Behavior Map (?)  
In each case, the layout is represented as a grid of spinboxes with the values inside being the values for each screen.

### Layout 0

This is the main layout of the level, the layer that has collision and that the player interacts with.

Here, the values represent an index into the list of screens available from the tileset file.

### Layouts 1-3

Those layouts may be used for parallax background or foreground, in no particular order.

### Camera Scroll Layout

This layout determines how the camera should treat each screen of the level.  
It appears this follows the same code as in [Mega Man Zero 3](https://coltaho.com/ZeroEditor/Zero3_ReadMe.html)  
- 0x0-0xD: Free range (will not scroll to screens with IDs different by 2 or more until the player goes in them)
- 0xE: Sky (camera does not scroll to the screen, but the player can move freely)
- 0xF: Kill zone

> [!NOTE]
> Some configurations may cause the level to be unable to load.  
> I am not sure why, but so far it seems to occur whenever a Free range screen value differs from the adjacent screens by more than 2, or when a 0xE screen has Free range screens over it.

### Radar Scope Layout

This is the screen layout that you will see on the sub-screen of the DS when using Model P or Model L.

### Tileset Offset Map

This map controls the graphics swap in the tileset from screen to screen.  
The game will load the tileset based on the leftmost visible screen.

### Behavior Map?

This appears to be what controls the role of the layers other than layer 0. It seems to have something to do with parallax.

## Entities

> [!WARNING]
> Modifying entities may or may not cause the game to be unable to load the level.  
> I am not sure why this happens even with what seems to be harmless modifications, but it may be a good idea to make backups before changing anything here.

Entities can be enemies, doors, NPCs, and really anything else that isn't static that the player can directly interact with.  
In levels, entities are ordered from top to bottom, then left to right.  
The entity data is stored in the level overlay.

You can choose to or not to load entities with the checkbox labeled "Load Entities".

> [!NOTE]
> The "Load Entity Graphics" feature is still very experimental, and in case of conflict, always rely on the information provided by mouse hover or by the left panel, after selecting the entity.

In this tab, there are two tabs: Coordinates and Slot data.  
To enable editing any of the values inside, you must first select an entity by clicking on it. Entities have the appearance of a blue square with a green number inside.

### Coordinates

This is the entity-specific data.

The "Entity Index" label tells you what entity is currently selected with a zero-based index (However the first and last ones are not displayed because they are more like start and end delimiters).

The spinboxes labeled "X" and "Y" control the entity's position. The X position has a much larger value range than the Y position.

The spinbox labeled "Slot" allows you to select what entity definition should be used for this entity.

### Slot Data

This is shared data.

The spinboxes allow you to modify the data structure, but I barely know what most of the data in it is for.

# Applying Tweaks

Tweaks are modifications you can make to the game's constants, which are stored in ARM9 overlays.  
Currently, only the "Physics" tab has patches.

The dropdown allows to select the topic of the tweaks.  
When done modifying the values, click on "Apply Tweaks" to confirm.

> [!NOTE]
> Depending on the game, there may not be any tweaks available.  
> The dropdown may also be empty if no categories were made for that game.

# Applying Patches

Tick or untick the patches as desired to enable or disable them.  
Some patches can also be expanded to see the smaller patches required to get the end result.

When done, click on "Apply Patches" to confirm.

> [!NOTE]
> Depending on the game, there may not be any patches available.