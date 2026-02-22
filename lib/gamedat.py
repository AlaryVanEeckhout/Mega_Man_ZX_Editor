# patches database
import enum
from . import dialogue

# indicators determine what the file most likely contains based on its name
I_GFX = ("_fnt",)
I_GFX_ZX = ("_fnt", "face", "title", "bbom", "dm", "elf", "g_", "game_parm", "lmlevel", "miss", "repair", "sec_disk", "sub")
I_GFX_ZXA = ("_fnt", "face", "title", "cmm_", "ls_", "sub_")
I_FONT = ("font",)
I_DIALOGUE = ("talk", "m_")
I_PANM = ("panm",)
I_MUGSHOT = ("face",)
# relative ROM pointers to uncompressed ARM9
ARM9_ZX_E = {"entity": 0x000C9C7C, #each entry is 0x4*levelOverlayCount bytes
             "level": 0x000CB9D4,
             "dialogue box" : 0x000BEC8C,
             "dialogue names jp": 0x000BF5CC,
             "dialogue names en": 0x000BF9EC,
             "dialogue font": 0x000BFE0C}
ARM9_ZX_J = {"entity": 0x000C685C,
             "level": 0x000C7E88,
             "dialogue box" : 0x000BEAD8, # gfx split in two places???
             "dialogue names jp": 0x000BE6B8,
             "dialogue names en": 0,
             "dialogue font": 0x000BF118}
ARM9_ZXA_E = {"entity": 0x000FCE94,
              "level": 0x000FEFD4,
              "dialogue box" : 0x000DC52C,
              "dialogue names jp": 0x000DBC2C,
              "dialogue names en": 0x000DC0AC,
              "dialogue font": 0x000DCF6C}
ARM9_ZXA_J = {"entity": 0x000FDC9C,
              "level": 0x000FF55C,
              "dialogue box" : 0x000DEF28,
              "dialogue names jp": 0x000DEAA8,
              "dialogue names en": 0,
              "dialogue font": 0x000DF968}
# add dicts for charmaps? (en, jp, names en, names jp)
CHARMAPS_ZX = {"en": dialogue.CHARMAP_DIALOGUE_ZX_EN,
               "jp": dialogue.CHARMAP_DIALOGUE_ZX_JP,
               "names en": dialogue.CHARMAP_DIALOGUENAME_ZX_EN,
               "names jp": dialogue.CHARMAP_DIALOGUENAME_ZX_JP}
CHARMAPS_ZXA = {"en": dialogue.CHARMAP_DIALOGUE_ZX_EN,
                "jp": dialogue.CHARMAP_DIALOGUE_ZXA_JP,
                "names en": dialogue.CHARMAP_DIALOGUENAME_ZX_EN,
                "names jp": dialogue.CHARMAP_DIALOGUENAME_ZX_JP}

class GameEnum(enum.Enum):

  def __init__(self, id: enum.auto, arm9Addrs: int, charmaps: dict, fileIndicators: dict, patches: list[list]):
      self.id = id
      self.arm9Addrs = arm9Addrs
      self.charmaps = charmaps
      self.fileIndicators = fileIndicators
      self.patches = patches

  ROCKMANZX = enum.auto(), ARM9_ZX_J, CHARMAPS_ZX, {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, []
  MEGAMANZX = enum.auto(), ARM9_ZX_E, CHARMAPS_ZX, {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, [
    ["real patch test", "text", [0x021AE600, "talk_m01_en(Vent)", 'f11b58', '0-ffff'], [0x21B0400, "talk_m01_en(Aile)", 'ed1d58', 'f11b--']],
    [0x021AE600, "empty patch test", "empty", '', ''],
    [0x021AE600, "overwiting patch test", "text", 'f11b58', '202123'],
    [0x021AE600, "overwiting patch test", "text", 'f1', '20']
  ]

  ROCKMANZXA = enum.auto(), ARM9_ZXA_J, CHARMAPS_ZXA, {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  MEGAMANZXA = enum.auto(), ARM9_ZXA_E, CHARMAPS_ZXA, {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  # wildcard so that the keys in the fileIndicators dict can still be accessed for unsupported games
  UNSUPPORTED = enum.auto(), {"entity": 0,
                              "level": 0,
                              "dialogue box" : 0,
                              "dialogue names jp": 0,
                              "dialogue names en": 0,
                              "dialogue font": 0
                         }, CHARMAPS_ZX, {"Graphics" : I_GFX,
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