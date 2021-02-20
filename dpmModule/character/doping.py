from ..kernel.core import ExtendedCharacterModifier as ExMDF


class Doping:
    dopingListAtt = {
        "길드의 더 큰 축복": ExMDF(att=30),  # Guild Blessing
        "우뿌": ExMDF(att=30),  # ??
        "붕뿌": ExMDF(att=30),  # ??
        "유니온의 힘": ExMDF(att=30),  # Legion Coupon
        "익스레드/블루": ExMDF(att=30),  # Monster Park
        "MVP 버프": ExMDF(att=30),  # MVP Superpower
        "영웅의 메아리": ExMDF(patt=4),  # Heroes Echo
        # "이벤트 버프": ExMDF(att=20, armor_ignore=30, boss_pdamage=30, stat_main=40, stat_sub=40)
    }

    dopingListStat = {"향상된 10단계 물약": ExMDF(stat_main=30)}  # Tier 10 potion
    dopingListXenon = {"향상된 10단계 물약": ExMDF(stat_main=30*3)}  # Tier 10 potion for xenon
    dopingListHP = {"익스트림 레드": ExMDF(stat_main=2000)}  # Monster Park

    dopingListDamage = {
        "노블레스(뎀퍼)": ExMDF(pdamage=30),  # Guild Skill Nobelesse
        "노블레스(보공)": ExMDF(boss_pdamage=28),  # Guild Skill
        "반빨별": ExMDF(boss_pdamage=20),  # ??
    }

    dopingListArmor = {"고관비": ExMDF(armor_ignore=20)} # ??

    dopingListCritDamage = {"노블레스(크뎀)": ExMDF(crit_damage=30)}  # Guild Skill

    @staticmethod
    def get_full_doping(jobtype: str) -> ExMDF:
        retMdf = ExMDF()

        for name in Doping.dopingListAtt:
            retMdf = retMdf + Doping.dopingListAtt[name]
        if jobtype == "xenon":
            for name in Doping.dopingListXenon:
                retMdf = retMdf + Doping.dopingListXenon[name]
        elif jobtype == "HP":
            for name in Doping.dopingListHP:
                retMdf = retMdf + Doping.dopingListHP[name]
        else:
            for name in Doping.dopingListStat:
                retMdf = retMdf + Doping.dopingListStat[name]
        for name in Doping.dopingListDamage:
            retMdf = retMdf + Doping.dopingListDamage[name]
        for name in Doping.dopingListArmor:
            retMdf = retMdf + Doping.dopingListArmor[name]
        for name in Doping.dopingListCritDamage:
            retMdf = retMdf + Doping.dopingListCritDamage[name]

        return retMdf
