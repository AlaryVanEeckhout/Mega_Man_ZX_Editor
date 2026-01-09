# patches database
import enum

# indicators determine what the file most likely contains based on its name
I_GFX = ("_fnt",)
I_GFX_ZX = ("_fnt", "face", "title", "bbom", "dm", "elf", "g_", "game_parm", "lmlevel", "miss", "repair", "sec_disk", "sub")
I_GFX_ZXA = ("_fnt", "face", "title", "cmm_", "ls_", "sub_")
I_FONT = ("font",)
I_DIALOGUE = ("talk", "m_")
I_PANM = ("panm",)
I_MUGSHOT = ("face",)
# level layout arm9 overlay struct RAM pointers
LEVEL_ZX = 0x020CB9D4
LEVEL_ZXA = 0x020FECD4

class GameEnum(enum.Enum):

  def __init__(self, id: enum.auto, ovlStructtableAddr: int, fileIndicators: dict, patches: list[list]):
      self.id = id
      self.ovlStructtableAddr = ovlStructtableAddr
      self.fileIndicators = fileIndicators
      self.patches = patches

  ROCKMANZX = enum.auto(), LEVEL_ZX, {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, []
  MEGAMANZX = enum.auto(), LEVEL_ZX, {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, [
    ["real patch test", "text", [0x021AE600, "talk_m01_en(Vent)", 'f11b58', '0-ffff'], [0x21B0400, "talk_m01_en(Aile)", 'ed1d58', 'f11b--']],
    [0x021AE600, "empty patch test", "empty", '', ''],
    [0x021AE600, "overwiting patch test", "text", 'f11b58', '202123'],
    [0x021AE600, "overwiting patch test", "text", 'f1', '20']
  ]

  ROCKMANZXA = enum.auto(), LEVEL_ZXA, {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  MEGAMANZXA = enum.auto(), LEVEL_ZXA, {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  # wildcard so that the keys in the fileIndicators dict can still be accessed for unsupported games
  UNSUPPORTED = enum.auto(), 0, {"Graphics" : I_GFX,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []

# Notes:
# format 1 = [Address, Name, Type, OGData, NewData]
# format 2 = [Name, Type, [Address, Name, OGData, NewData]]
#
#   - you can use "-" to indicate that the hex digit must not be replaced
#