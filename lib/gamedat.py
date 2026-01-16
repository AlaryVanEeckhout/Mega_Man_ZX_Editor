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
ARM9_ZX = {"level": 0x020CB9D4,
           "dialogue box" : 0x020BEC8C,
           "dialogue names": 0x020BF5EC,
           "dialogue font": 0x020BFE0C}
ARM9_ZXA = {"level": 0x020FEFD4,
            "dialogue box" : 0x020DC52C,
            "dialogue names": 0x020DBC2C,
            "dialogue font": 0x020DCF6C}

class GameEnum(enum.Enum):

  def __init__(self, id: enum.auto, arm9Addrs: int, fileIndicators: dict, patches: list[list]):
      self.id = id
      self.arm9Addrs = arm9Addrs
      self.fileIndicators = fileIndicators
      self.patches = patches

  ROCKMANZX = enum.auto(), ARM9_ZX, {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, []
  MEGAMANZX = enum.auto(), ARM9_ZX, {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, [
    ["real patch test", "text", [0x021AE600, "talk_m01_en(Vent)", 'f11b58', '0-ffff'], [0x21B0400, "talk_m01_en(Aile)", 'ed1d58', 'f11b--']],
    [0x021AE600, "empty patch test", "empty", '', ''],
    [0x021AE600, "overwiting patch test", "text", 'f11b58', '202123'],
    [0x021AE600, "overwiting patch test", "text", 'f1', '20']
  ]

  ROCKMANZXA = enum.auto(), ARM9_ZXA, {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  MEGAMANZXA = enum.auto(), ARM9_ZXA, {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  # wildcard so that the keys in the fileIndicators dict can still be accessed for unsupported games
  UNSUPPORTED = enum.auto(), {"level": 0,
                              "dialogue box" : 0,
                              "dialogue names": 0,
                              "dialogue font": 0
                         }, {"Graphics" : I_GFX,
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