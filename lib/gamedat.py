# patches database
import enum

# indicators determine what the file most likely contains based on its name
I_GFX_ZX = ("face", "obj_fnt", "title", "bbom", "dm23", "elf", "g_", "game_parm", "lmlevel", "miss", "repair", "sec_disk", "sub")
I_GFX_ZXA = ("face", "obj_fnt", "title", "cmm_frame_fnt", "cmm_mega_s", "cmm_rock_s", "ls_", "sub_db", "sub_oth")
I_FONT = ("font",)
I_DIALOGUE = ("talk", "m_")
I_PANM = ("panm",)
I_MUGSHOT = ("face",)

class GameEnum(enum.Enum):

  def __init__(self, id: enum.auto, fileIndicators: dict, patches: list[list]):
      self.id = id
      self.fileIndicators = fileIndicators
      self.patches = patches

  ROCKMANZX = enum.auto(), {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, []
  MEGAMANZX = enum.auto(), {"Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT}, [
    ["real patch test", "text", [0x021AE600, "talk_m01_en(Vent)", 'f11b58', '0-ffff'], [0x21B0400, "talk_m01_en(Aile)", 'ed1d58', 'f11b--']],
    [0x021AE600, "empty patch test", "empty", '', ''],
    [0x021AE600, "overwiting patch test", "text", 'f11b58', '202123'],
    [0x021AE600, "overwiting patch test", "text", 'f1', '20']
  ]

  ROCKMANZXA = enum.auto(), {"Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT}, []
  MEGAMANZXA = enum.auto(), {"Graphics" : I_GFX_ZXA,
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