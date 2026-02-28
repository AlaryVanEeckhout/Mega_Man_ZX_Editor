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
ENTITYKINDS_ZX = {
                0x02:("Enemy", {
                    0x00: ("Eyeballoon", {}),
                    0x01: ("Crickaleap", {}),
                    0x02: ("Galleon Hunter", {}),
                    0x03: ("Whirling 44", {}),
                    0x05: ("Presto Cannon", {}),
                    0x07: ("Tornado Fencer", {}),
                    0x09: ("Sphenalauncher", {}),
                    0x0B: ("Cutting Gyro", {}),
                    0x0C: ("Auto Counter", {
                       0x00:("ECO",{}),
                       0x01:("POP",{})
                    }),
                    0x0D: ("Mechadragon", {}),
                    0x1A: ("Pattrolaur", {}),
                    0x1B: ("Warp Prism", {}),
                    0x1F: ("Shrimpstroke", {}),
                    0x21: ("Springer", {
                       0x01:("N/A",{
                          0x00:("Normal",{}),
                          0x01:("Spawner",{})
                       })
                    }),
                    0x22: ("Valkyraffe", {}),
                    0x26: ("Exhausted Guardian", {}), # Why is that an enemey?
                    0x28: ("Capsule Shooter", {}),
                    0x29: ("Elemental Face", {
                       0x00:("Heat",{}),
                       0x01:("Shock",{}),
                       0x01:("Frozen",{})
                    }),
                    0x2B: ("Bora Bora", {}),
                    0x2C: ("Angle Cannon", {}),
                    0x2E: ("Releaf", {}),
                    0x32: ("Galleon Diver", {}),
                    0x34: ("Galleon Burner", {}),
                    0x35: ("Energy Cannon", {}),
                    0x36: ("Buoybuoy", {}),
                    0x37: ("Carom", {}),
                    0x38: ("Rattrap", {}),
                    0x3A: ("Elemental Dart", {
                       0x00:("Fire",{}),
                       0x01:("Electric",{})
                    }),
                    0x3B: ("Batty", {}),
                    0x3C: ("Web Bolt", {}),
                    0x45: ("Spi-King", {}),
                    0x47: ("Bambooloss", {})
                }),
                0x05:("Background", {
                   0x01: ("Door/Switch Mechanism", {
                      0x00:("Door",{}),
                      0x01:("Switch",{})
                   }),
                   0x02: ("Electric Truck", {}),
                   0x03: ("Area E Generator", {}),
                   0x04: ("Compactor", {}),
                   0x05: ("Electric Rods", {
                      0x00: ("Anti-clockwise", {}),
                      0x01: ("Clockwise", {})
                   }),
                   0x06: ("Electric Spark", {
                      0x00:("Right",{}),
                      0x01:("Left",{}),
                      0x02:("Down",{}),
                      0x03:("Up",{})
                   }),
                   0x08: ("Electric Rod button", {}),
                   0x08: ("Giant Gear", {
                      0x00: ("Normal", {}),
                      0x01: ("Offset", {})
                   }),
                   0x0B: ("Fire thorns", {}),
                   0X0C: ("Cat", {}),
                   0x0D: ("Fountain top", {}),
                   0x0F: ("Box", {}),
                   0x10: ("King Flyer Bridge", {}),
                   0x12: ("Sidescroll door", {}),
                   0x13: ("Fade out/in door", {
                      None:("*",{
                         0x00:("White",{}),
                         0x01:("Red",{}),
                         0x02:("Blue",{}),
                         0x03:("Purple",{}),
                         0x04:("Yellow",{}),
                         0x05:("Green",{}),
                         0x0A:("Power Plant",{})
                      }),
                   }),
                   0x14: ("Punchable Tree", {}),
                   0x17: ("Electric Platform", {
                      0x00:("Platform",{}),
                      0x01:("Floor",{})
                   }),
                   0x19: ("Dynamic Background", {
                      0x02:("Crumble bridge",{}),
                      0x03:("Slither Inc. door",{}) # maybe?
                   }),
                   0x1B: ("Bridge switch", {}),
                   0x1C: ("Transerver", {
                      0x00:("Teleporter",{}),
                      0x01:("Computer",{})
                   }),
                   0x22: ("Witch", {}),
                   0x25: ("Ice Cube", {}),
                   0x27: ("Crickaleap Dumper", {}),
                   0x2E: ("Area J Sled", {}),
                   0x31: ("Destructible Container", {
                      0x00:("Barrel",{}),
                      0x01:("Crate",{})
                   }),
                   0x33: ("Platform Cannon", {}), # does the platform spawn the cannon?
                   0x35: ("Galleon Sledder", {}),
                   0x3D: ("Red Striker", {}),
                   0x43: ("Disappearing platforms", {}),
                   0x48: ("Guardian", {
                      0x01:("0x01",{
                         0x03:("Cédre",{})
                      }),
                      0x04:("Operator",{
                        0x00:("Tulip",{}),
                        0x01:("Gardénia",{}),
                        0x02:("Marguerite",{})
                      })
                   }),
                   0x49: ("Townspeople", {}),
                   0x50: ("Boss Trophee", {
                      0x00:("Hivolt",{}),
                      0x01:("Lurerre",{}),
                      0x02:("Fistleo",{}),
                      0x03:("Purprill",{}),
                      0x04:("Hurricaune",{}),
                      0x05:("Leganchor",{}),
                      0x06:("Flammole",{}),
                      0x07:("Protectos",{})
                   }),
                   0x54: ("Arcade", {}),
                   0x57: ("Opening Guardian", {
                      0x00:("Prairie",{}),
                      0x01:("Bar",{}),
                      0x02:("Maquereau",{})
                   }),
                   0x59: ("Prairie (Grand Nuage)", {}),
                   0x5B: ("Test Guardian", {}) # might be something more generic that is used for Guardian test
                }),
                0x06:("Item", {
                   0x00: ("Refill", {
                      0x01:("Medium Health", {}),
                      0x02:("Large Health", {}),
                      0x04:("Weapon Energy", {}),
                      0x06:("E-Crystal", {}),
                      0x07:("Life", {}),
                   }),
                   0x01: ("Secret Disk", {
                    0x00:("Bosses (B)", {}),
                    0x01:("Enemy A (M)", {}),
                    0x02:("Enemy B (E)", {}),
                    0x03:("Others (O)", {})
                   }),
                   0x02: ("Expansion", {
                      0x00:("Life-Up (Area D)", {}),
                      0x02:("Life-Up (Area J)", {}),
                      0x08:("Sub-Tank (Area A)", {}),
                      0x09:("Sub-Tank (Area E)", {}),
                   })
                })
}
ENTITYKINDS_ZXA = {
                0x02:("Enemy", {
                   0x36: ("Mega Man a", {
                      0x00:("Galleon Hunter", {}),
                      0x01:("Mettaur", {}),
                      0x02:("Carom", {}),
                      0x03:("Crickaleap", {}),
                      0x04:("MachYOS", {}),
                      0x05:("Gyrocutter", {})
                   }),
                }),
                0x05:("Background", {
                   0x12: ("Sidescroll door", {}),
                   0x13: ("Fade out/in door", {})
                }),
                0x06:("Item", {
                })
}


class GameEnum(enum.Enum):

  def __init__(self, id: enum.auto, arm9Addrs: int, charmaps: dict[str, dialogue.CharMap], fileIndicators: dict[str, tuple], entityNames: dict[str, dict], patches: list[list]):
      self.id = id
      self.arm9Addrs = arm9Addrs
      self.charmaps = charmaps
      self.fileIndicators = fileIndicators
      self.entityNames = entityNames
      self.patches = patches

  ROCKMANZX = enum.auto(), ARM9_ZX_J, CHARMAPS_ZX, {
                            "Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT
                            }, ENTITYKINDS_ZX, []
  MEGAMANZX = enum.auto(), ARM9_ZX_E, CHARMAPS_ZX, {
                            "Graphics" : I_GFX_ZX,
                            "Font" : I_FONT,
                            "Dialogue" : I_DIALOGUE,
                            "Palette Animation" : I_PANM,
                            "Mugshot" : I_MUGSHOT
                            }, ENTITYKINDS_ZX, [
    ["real patch test", "text", [0x021AE600, "talk_m01_en(Vent)", 'f11b58', '0-ffff'], [0x21B0400, "talk_m01_en(Aile)", 'ed1d58', 'f11b--']],
    [0x021AE600, "empty patch test", "empty", '', ''],
    [0x021AE600, "overwiting patch test", "text", 'f11b58', '202123'],
    [0x021AE600, "overwiting patch test", "text", 'f1', '20']
  ]

  ROCKMANZXA = enum.auto(), ARM9_ZXA_J, CHARMAPS_ZXA, {
                             "Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT
                             }, ENTITYKINDS_ZXA, []
  MEGAMANZXA = enum.auto(), ARM9_ZXA_E, CHARMAPS_ZXA, {
                             "Graphics" : I_GFX_ZXA,
                             "Font" : I_FONT,
                             "Dialogue" : I_DIALOGUE,
                             "Palette Animation" : I_PANM,
                             "Mugshot" : I_MUGSHOT
                             }, ENTITYKINDS_ZXA, []
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
                             "Mugshot" : I_MUGSHOT}, ENTITYKINDS_ZX, []

# Notes:
# format 1 = [Address, Name, Type, OGData, NewData]
# format 2 = [Name, Type, [Address, Name, OGData, NewData]]
#
#   - you can use "-" to indicate that the hex digit must not be replaced
#