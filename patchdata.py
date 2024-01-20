import enum

class GameEnum(enum.Enum):

  def __init__(self, id, patches):
      self.id = id
      self.patches = patches

  MEGAMANZX = enum.auto(), [
    #Address, Name, Type, OGData, NewData
    [0x00000000, "enum is working", "text", b'', b''],
    [0x00000000, "patch test1", "text", b'0', b'0'],
    [0x00000000, "patch test2", "text", b'00', b'00']
  ]
  MEGAMANZXA = enum.auto(), []