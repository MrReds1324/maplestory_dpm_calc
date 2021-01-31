from ..kernel.core import ExtendedCharacterModifier as ExMDF


class Doping:
    dopingListAtt = {
        "길드의 축복": ExMDF(att=20),  # Guild's Blessing
        "우뿌": ExMDF(att=30),  # Ursus buff?
        "익스레드/블루": ExMDF(att=30),  # Red/Blue monster park potions?
        "MVP 버프": ExMDF(att=30),  # MVP superpower buff
        "영웅의 메아리": ExMDF(patt=4),  # Heroes Echo
    }

    dopingListStat = {"향상된 10단계 물약": ExMDF(stat_main=30)}  # Enhanced Tier 10 Potion?

    dopingListDamage = {
        "노블레스(뎀퍼)": ExMDF(pdamage=30),  # Guild Skill Nobelesse
        "노블레스(보공)": ExMDF(boss_pdamage=28),  # Guild Skill
        "반빨별": ExMDF(boss_pdamage=20),  # ??
    }

    dopingListArmor = {"고관비": ExMDF(armor_ignore=20)} # ??

    dopingListCritDamage = {"노블레스(크뎀)": ExMDF(crit_damage=30)}  # Guild Skill

    @staticmethod
    def get_full_doping() -> ExMDF:
        retMdf = ExMDF()

        for name in Doping.dopingListAtt:
            retMdf = retMdf + Doping.dopingListAtt[name]
        for name in Doping.dopingListStat:
            retMdf = retMdf + Doping.dopingListStat[name]
        for name in Doping.dopingListDamage:
            retMdf = retMdf + Doping.dopingListDamage[name]
        for name in Doping.dopingListArmor:
            retMdf = retMdf + Doping.dopingListArmor[name]
        for name in Doping.dopingListCritDamage:
            retMdf = retMdf + Doping.dopingListCritDamage[name]

        return retMdf
