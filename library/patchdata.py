import enum

class GameEnum(enum.Enum):

  def __init__(self, id: enum.auto, patches: list):
      self.id = id
      self.patches = patches

  MEGAMANZX = enum.auto(), [
    #Address, Name, Type, OGData, NewData
    [0x021AE600, "real patch test", "text", bytes.fromhex('f11b58'), bytes.fromhex('0fffff')],
    [0x021AE600, "empty patch test", "empty", bytes.fromhex(''), bytes.fromhex('')],
    [0x021AE600, "overwiting patch test", "text", bytes.fromhex('f11b58'), bytes.fromhex('202123')],
    [0x021AE600, "overwiting patch test", "text", bytes.fromhex('f1'), bytes.fromhex('20')]
  ]
  MEGAMANZXA = enum.auto(), []