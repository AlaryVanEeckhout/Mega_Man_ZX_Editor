from .charmap import CharMap


CHARMAP_DIALOGUE_ZX_EN = CharMap()
CHARMAP_DIALOGUE_ZX_EN.add_mapping_range((0x00,), " ", 0x5f)
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x5f,), "⠂")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x60,), "€")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x61,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x62,), "𐄀")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x63,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x64,), "⠤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x65,), "┅")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x66,), "") #unknown char, empty in font
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x67,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x68,), "ˆ")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x69,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x6a,), "Š")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x6b,), "⟨")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x6c,), "Œ")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x6d,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x6e,), "Ž")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x6f,), "") #unknown char, empty in font
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x70,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x71,), "‘")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x72,), "’")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x73,), "“")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x74,), "”")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x75,), "•")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x76,), "") #unknown char, empty in font
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x77,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x78,), "˜")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x79,), "™")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x7a,), "š")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x7b,), "⟩")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x7c,), "œ")
#CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x7d,), "") #unknown char, empty in font
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x7e,), "ž")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x7f,), "Ÿ")

CHARMAP_DIALOGUE_ZX_EN.add_mapping_range((0x81,), "¡", 3)

CHARMAP_DIALOGUE_ZX_EN.add_mapping_range((0x88,), "¨", 4)

CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x8e,), "®")

CHARMAP_DIALOGUE_ZX_EN.add_mapping_range((0x90,), "°", 2)

CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x94,), "´")

CHARMAP_DIALOGUE_ZX_EN.add_mapping((0x97,), "·")

CHARMAP_DIALOGUE_ZX_EN.add_mapping_range((0x9a,), "º", 2)

CHARMAP_DIALOGUE_ZX_EN.add_mapping_range((0x9f,), "¿", 0x41)
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe0,), "├DPAD_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe1,), "├DPAD_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe2,), "├BUTTON_A_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe3,), "├BUTTON_A_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe4,), "├BUTTON_B_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe5,), "├BUTTON_B_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe6,), "├BUTTON_X_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe7,), "├BUTTON_X_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe8,), "├BUTTON_Y_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xe9,), "├BUTTON_Y_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xea,), "├BUTTON_L_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xeb,), "├BUTTON_L_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xec,), "├BUTTON_R_LEFT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xed,), "├BUTTON_R_RIGHT┤")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xee,), "🡅")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xef,), "🡇")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xf0, 0x00), "🡄")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xf0, 0x01), "🡆")
CHARMAP_DIALOGUE_ZX_EN.add_mapping((0xf0, 0x02), "⯈")


CHARMAP_DIALOGUE_ZX_JP = CharMap()
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0x00,), "　")
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0x01,), "０", 0xa)
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0x0b,), "Ａ", 0x1a)
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0x25,), "ａ", 0x1a)
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0x3f,), "ー")
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0x40,), "ぁ", 0x4f)
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0x8f,), "を", 2)
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0x91,), "ァ", 0x4f)
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0xe0,), "ヲ", 5)
CHARMAP_DIALOGUE_ZX_JP.add_mapping_range((0xe5,), "！", 0xb)
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x00), "、")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x01), "‐")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x02), "。")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x03), "／")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x04), "：")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x05), "〈")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x06), "＝")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x07), "〉")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x08), "？")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x09), "［")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x0A), "］")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x0B), "＿")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x0C), "～")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x0D), "「")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x0E), "」")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x0F), "…")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x10), "運")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x11), "屋")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x12), "部")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x13), "隊")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x14), "合")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x15), "流")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x16), "本")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x17), "社")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x18), "何")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x19), "者")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x1A), "出")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x1B), "現")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x1C), "原")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x1D), "因")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x1E), "調")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x1F), "査")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x20), "子")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x21), "生")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x22), "命")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x23), "体")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x24), "戦")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x25), "争")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x26), "発")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x27), "地")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x28), "見")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x29), "会")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x2A), "国")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x2B), "助")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x2C), "年")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x2D), "新")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x2E), "今")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x2F), "回")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x30), "変")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x31), "身")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x32), "少")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x33), "女")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x34), "転")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x35), "送")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x36), "青")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x37), "赤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x38), "上")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x39), "後")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x3A), "世")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x3B), "界")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x3C), "進")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x3D), "化")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x3E), "王")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x3F), "人")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x40), "間")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x41), "数")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x42), "百")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x43), "支")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x44), "配")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x45), "男")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x46), "勇")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x47), "気")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x48), "前")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x49), "闘")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x4A), "用")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x4B), "時")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x4C), "代")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x4D), "平")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x4E), "和")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x4F), "死")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x50), "名")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x51), "・") # maybe?
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x52), "血")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x53), "下")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x54), "左")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x55), "右")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x56), "├DPAD┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x57), "├BUTTON_A┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x58), "├BUTTON_B┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x59), "├BUTTON_X┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x5A), "├BUTTON_Y┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x5B), "├BUTTON_L┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x5C), "├BUTTON_R┤")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x5D), "中")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x5E), "開")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x5F), "分")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x60), "型")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x61), "長")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x62), "大")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x63), "量")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x64), "内")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x65), "同")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x66), "動")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x67), "続")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x68), "悪")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x69), "活")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x6A), "利")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x6B), "空")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x6C), "日")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x6D), "産")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x6E), "使")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x6F), "単")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x70), "天")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x71), "井")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x72), "火")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x73), "玉")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x74), "一")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x75), "定")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x76), "方")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x77), "向")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x78), "背")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x79), "水")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x7A), "両")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x7B), "各")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x7C), "古")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x7D), "電")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x7E), "固")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x7F), "止")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x80), "在")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x81), "—") # maybe?
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x82), "–") # maybe?
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x83), "仲")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x84), "強")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x85), "力")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x86), "面")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x87), "小")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x88), "所")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x89), "目")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x8A), "々")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x8B), "都")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x8C), "市")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x8D), "伝")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x8E), "説")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x8F), "入")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x90), "魚")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x91), "路")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x92), "守")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x93), "手")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x94), "木")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x95), "葉")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x96), "囗")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x97), "重")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x98), "半")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x99), "正")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x9A), "式")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x9B), "．")
CHARMAP_DIALOGUE_ZX_JP.add_mapping((0xf0, 0x9C), "⯈")

CHARMAP_DIALOGUE_ZXA_DS = CharMap()

CHARMAP_DIALOGUE_ZXA_JP = CharMap()

CHARMAP_DIALOGUENAME_ZX_EN = CharMap()
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping_range((0x00,), " ", 0x5b)
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x5b,), "é")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x5c,), "ê")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x5d,), "ア") # AIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x5e,), "イ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x5f,), "ウ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x60,), "エ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x61,), "オ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x62,), "ァ") # aiueo
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x63,), "ィ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x64,), "ゥ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x65,), "ェ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x66,), "ォ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x67,), "ヴ") # VU
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x68,), "カ") # KAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x69,), "キ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x6a,), "ク")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x6b,), "ケ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x6c,), "コ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x6d,), "ガ") # GAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x6e,), "ギ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x6f,), "グ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x70,), "ゲ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x71,), "ゴ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x72,), "サ") # SAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x73,), "シ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x74,), "ス")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x75,), "セ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x76,), "ソ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x77,), "ザ") # ZAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x78,), "ジ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x79,), "ズ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x7a,), "ゼ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x7b,), "ゾ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x7c,), "タ") # TAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x7d,), "チ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x7e,), "ツ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x7f,), "テ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x80,), "ト")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x81,), "ダ") # DAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x82,), "ヂ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x83,), "ヅ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x84,), "デ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x85,), "ド")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x86,), "ッ") # sokuon
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x87,), "ナ") # NAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x88,), "ニ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x89,), "ヌ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x8a,), "ネ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x8b,), "ノ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x8c,), "ハ") # HAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x8d,), "ヒ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x8e,), "フ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x8f,), "へ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x90,), "ホ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x91,), "バ") # BAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x92,), "ビ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x93,), "ブ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x94,), "べ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x95,), "ボ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x96,), "パ") # PAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x97,), "ピ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x98,), "プ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x99,), "ペ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x9a,), "ポ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x9b,), "マ") # MAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x9c,), "ミ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x9d,), "ム")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x9e,), "メ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0x9f,), "モ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa0,), "ヤ") # YAUO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa1,), "ユ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa2,), "ヨ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa3,), "ャ") # yauo
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa4,), "ュ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa5,), "ョ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa6,), "ラ") # RAIUEO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa7,), "リ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa8,), "ル")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xa9,), "レ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xaa,), "ロ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xab,), "ワ") # WAO
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xac,), "ヲ")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xad,), "ン") # N
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping_range((0xae,), "Ａ", 0x1a)
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xc8,), "－")
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping_range((0xc9,), "０", 0xa)
CHARMAP_DIALOGUENAME_ZX_EN.add_mapping((0xd3,), "？")

CHARMAP_DIALOGUENAME_ZX_JP = CharMap()
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x00,), "ア") # AIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x01,), "イ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x02,), "ウ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x03,), "エ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x04,), "オ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x05,), "ァ") # aiueo
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x06,), "ィ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x07,), "ゥ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x08,), "ェ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x09,), "ォ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x0a,), "ヴ") # VU
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x0b,), "カ") # KAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x0c,), "キ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x0d,), "ク")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x0e,), "ケ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x0f,), "コ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x10,), "ガ") # GAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x11,), "ギ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x12,), "グ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x13,), "ゲ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x14,), "ゴ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x15,), "サ") # SAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x16,), "シ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x17,), "ス")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x18,), "セ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x19,), "ソ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x1a,), "ザ") # ZAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x1b,), "ジ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x1c,), "ズ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x1d,), "ゼ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x1e,), "ゾ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x1f,), "タ") # TAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x20,), "チ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x21,), "ツ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x22,), "テ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x23,), "ト")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x24,), "ダ") # DAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x25,), "ヂ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x26,), "ヅ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x27,), "デ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x28,), "ド")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x29,), "ッ") # sokuon
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x2a,), "ナ") # NAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x2b,), "ニ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x2c,), "ヌ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x2d,), "ネ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x2e,), "ノ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x2f,), "ハ") # HAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x30,), "ヒ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x31,), "フ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x32,), "へ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x33,), "ホ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x34,), "バ") # BAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x35,), "ビ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x36,), "ブ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x37,), "べ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x38,), "ボ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x39,), "パ") # PAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x3a,), "ピ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x3b,), "プ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x3c,), "ペ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x3d,), "ポ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x3e,), "マ") # MAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x3f,), "ミ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x40,), "ム")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x41,), "メ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x42,), "モ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x43,), "ヤ") # YAUO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x44,), "ユ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x45,), "ヨ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x46,), "ャ") # yauo
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x47,), "ュ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x48,), "ョ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x49,), "ラ") # RAIUEO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x4a,), "リ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x4b,), "ル")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x4c,), "レ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x4d,), "ロ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x4e,), "ワ") # WAO
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x4f,), "ヲ")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x50,), "ン") # N
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping_range((0x51,), "Ａ", 0x1a)
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x6b,), "－")
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping_range((0x6c,), "０", 0xa)
CHARMAP_DIALOGUENAME_ZX_JP.add_mapping((0x76,), "？")


for CHARMAP in [CHARMAP_DIALOGUE_ZX_EN, CHARMAP_DIALOGUE_ZX_JP, CHARMAP_DIALOGUE_ZXA_DS, CHARMAP_DIALOGUE_ZXA_JP]:
    CHARMAP.add_mapping((0xf1, None), "├COLOR 0x{0:02X}┤")
    CHARMAP.add_mapping((0xf2, None), "├PLACEMENT 0x{0:02X}┤")
    CHARMAP.add_mapping((0xf3, None), "├MUGSHOT 0x{0:02X}┤")
    CHARMAP.add_mapping((0xf4, None), "├ISOLATE 0x{0:02X}┤") #hides the next char and draws function arguments.
    CHARMAP.add_mapping((0xf5, None), "├REQUESTEND 0x{0:02X}┤") #same as 0xfe, but does not interrupt current dialogue
    CHARMAP.add_mapping((0xf6, None), "├TWOCHOICES 0x{0:02X}┤")
    CHARMAP.add_mapping((0xf7, None), "├ISOLATE2 0x{0:02X}┤") #same as 0xf4
    CHARMAP.add_mapping((0xf8, None), "├NAME 0x{0:02X}┤")
    CHARMAP.add_mapping((0xf9, None, None), "├COUNTER 0x{0:02X} 0x{1:02X}┤") #dialogue page counter???
    CHARMAP.add_mapping((0xfa,), "├PLAYERNAME┤") # writes player name
    CHARMAP.add_mapping((0xfb,), "├THREECHOICES┤")
    CHARMAP.add_mapping((0xfc,), "├NEWLINE┤")
    CHARMAP.add_mapping((0xfd,), "├NEWPAGE┤")
    CHARMAP.add_mapping((0xfe,), "├END┤")
    CHARMAP.add_mapping((0xff,), "├ENDOFFILE┤") #end of used file (duplicate text is used to fill the rest of the file)

for CHARMAP in [CHARMAP_DIALOGUENAME_ZX_EN, CHARMAP_DIALOGUENAME_ZX_JP]:
    CHARMAP.add_mapping((0xff,), "├ENDNAME┤")


class DialogueFile:
    def __init__(self, data: bytes, charmap: CharMap=CHARMAP_DIALOGUE_ZX_EN):
        self.charmap = charmap # en, jp, or names
        file_size = int.from_bytes(data[0x00:0x02], "little")
        text_bin_ptr_array_size = int.from_bytes(data[0x02:0x04], "little")
        assert file_size > text_bin_ptr_array_size

        data = data[0x04:file_size+0x04]
        assert data[len(data)-1] == 0xff

        text_bin_ptr_array = []
        for i in range(0, text_bin_ptr_array_size, 2):
            ptr = int.from_bytes(data[i:i+0x02], "little")
            assert ptr < (file_size - text_bin_ptr_array_size)
            text_bin_ptr_array.append(ptr)

        data = data[text_bin_ptr_array_size:]

        self.textAddress_list = []
        self.text_list = []
        self.text_id_list = []
        id = 0
        for i in range(len(text_bin_ptr_array)):
            start = text_bin_ptr_array[i]
            self.textAddress_list.append(start + text_bin_ptr_array_size + 0x04)
            if data[start] == 0xff:
                self.text_id_list.append(None)
                continue
            text = self.binToText_until_end(data[start:])
            if text in self.text_list:
                self.text_id_list.append(self.text_list.index(text))
                continue
            self.text_list.append(text)
            self.text_id_list.append(id)
            id += 1



    def binToText_until_end(self, data: bytearray) -> str: # used to convert individual messages in file
        text = ""
        while len(data) > 0:
            if data[0] == 0xFE: 
                return text
            t, l = self.charmap.get_byte_mapping(data)
            text += t
            data = data[l:]
        raise Exception("no end found for DialogueFile text")
        

    def binToText(data: bytearray, charmap: CharMap=CHARMAP_DIALOGUE_ZX_EN) -> str: # used when forcing dialogue display state
        text = ""
        while len(data) > 0:
            t, l = charmap.get_byte_mapping(data)
            text += t
            data = data[l:]
        return text


    def textToBin(data: str, charmap: CharMap=CHARMAP_DIALOGUE_ZX_EN) -> bytearray:
        bin = bytearray()
        while len(data) > 0:
            b, l = charmap.get_unicode_mapping(data)
            bin += b
            data = data[l:]
        return bin


    def toBytes(self):
        text_bin_list = []
        text_bin_id_ptr_list = []
        text_bin_size = 0
        for text in self.text_list:
            text_bin = DialogueFile.textToBin(text, self.charmap)
            text_bin_id_ptr_list.append(text_bin_size)
            text_bin_size += len(text_bin) + 1
            text_bin_list.append(text_bin)

        text_bin_ptr_array: list[int] = []
        for id in self.text_id_list:
            if id is None:
                text_bin_ptr_array.append(text_bin_size)
                continue
            text_bin_ptr_array.append(text_bin_id_ptr_list[id])

        text_bin_ptr_array_size = len(text_bin_ptr_array)*2
        file_size = text_bin_ptr_array_size + text_bin_size + 1

        assert file_size <= 0xffff

        file_binary = file_size.to_bytes(2, "little") + text_bin_ptr_array_size.to_bytes(2, "little")
        for ptr in text_bin_ptr_array:
            if ptr is None:
                file_binary += text_bin_size.to_bytes(2, "little")
                continue
            file_binary += ptr.to_bytes(2, "little")
        for text_bin in text_bin_list:
            file_binary += text_bin + 0xfe.to_bytes(1)
        return file_binary + 0xff.to_bytes(1)



 #create readable text
#with open("test.txt", "wb") as t:
#    t.write(bytes(DialogueFile.convertfile_bin_to_text("talk_m01_en1.bin"), "utf-8"))
 #create bin file
#with open("talk_m01_en1.bin", "wb") as t:
#    #DialogueFile.convertfile_text_to_bin("test.txt")
#    t.write((DialogueFile.convertfile_text_to_bin("test.txt")))