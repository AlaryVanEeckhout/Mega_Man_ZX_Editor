# Running the application

First you need to make sure the dependencies are installed. See [the "Setup for usage" section in README.md](https://github.com/AlaryVanEeckhout/Mega_Man_ZX_Editor/blob/main/README.md#setup-for-usage) for more information.  
To run the application, the file named "MME_NDS.py" must be run using python 3.

# Opening a ROM

Once the application is running, there are two ways to open a ROM.
1. In the File menu, click on the "Open" option with a folder icon
2. In the toolbar, click on the folder icon.

In both cases, a dialog will open, prompting you to open the desired ROM file.  
The dialog will only show files with the ".nds" or ".srl" extension, so if your ROM is in a zip file, you will have to extract it first.

Select the file, and click on the "Open" button.  
A progress bar will appear with the game's icon and title.

Once this progress bar disappears, the internal filesystem of the ROM will be displayed in a list on the left panel in the "File Explorer" tab.  
This means the ROM opened successfully.

> [!WARNING]
> If you try to open a ROM that is not supported by the editor, some features of the editor may not work as intended or the ROM may fail to open at all.

# Opening a file in the ROM

To open a file, simply click on it from the list of files.

By default, the application will try to guess what the file is and display its contents on the right panel accordingly.

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

## Font Files

## OAM Files

OAM stands for Object Attribute Memory.  
Each OAM file relies on a graphic file for rendering.  
The OAM file is called \<name\>_dat.bin and the associated graphic file is called \<name\>_fnt.bin

### Frames

### Animations

> [!WARNING]
> The saving of animations with removed or added frames is not yet on point, so avoid changing the amount of frames an animation has for now

## Model Files

# Editing a level

## Tileset

## Screens

## Entities

# Applying tweaks

# Applying patches