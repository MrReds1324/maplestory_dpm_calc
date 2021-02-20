from enum import Enum

from .globalSkill import GlobalSkills
from .jobbranch.thieves import ThiefSkills
from ..kernel import core
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import ComplexConditionRule, RuleSet, ConditionRule
from . import globalSkill
from .jobbranch import thieves
from . import jobutils
from math import ceil
from typing import Any, Dict

# TODO: Why is Retouda 5th order value 1,1, but Retouda passive is 2,2? 왜 레투다는 5차값이 1,1인데 레투다 패시브는 2,2일까?


# English skill information for Dual Blade here https://maplestory.fandom.com/wiki/Dual_Blade/Skills
class DualBladeSkills(Enum):
    # Link Skill
    ThiefsCunning = 'Thief\'s Cunning | 시프 커닝'
    # Rogue
    DarkSight = 'Dark Sight | 다크 사이트'
    FlashJump = 'Flash Jump | 플래시 점프'
    SideStep = 'Side Step | 사이드 스텝'
    BanditSlash = 'Bandit Slash | 샤프 슬래시'
    # Blade Recruit
    KataraMastery = 'Katara Mastery | 이도류 마스터리'
    SelfHaste = 'Self Haste | 셀프 헤이스트'
    TornadoSpin = 'Tornado Spin | 토네이도 스핀'
    # Blade Acolyte
    FatalBlow = 'Fatal Blow | 페이탈 블로우'
    SlashStorm = 'Slash Storm | 슬래시 스톰'
    ChannelKarma = 'Channel Karma | 카르마'
    KataraBooster = 'Katara Booster | 이도 부스터'
    PhysicalTraining = 'Physical Training | 피지컬 트레이닝'
    # Blade Specialist
    FlyingAssaulter = 'Flying Assaulter | 플라잉 어썰터'
    UpperStab = 'Upper Stab | 어퍼 스탭'
    Flashbang = 'Flashbang | 플래시 뱅'
    Venom = 'Venom | 베놈'
    # Blade Lord
    BloodyStorm = 'Bloody Storm | 블러디 스톰'
    BladeAscension = 'Blade Ascension | 블레이드 어센션'
    ChainsofHell = 'Chains of Hell | 사슬지옥'
    MirrorImage = 'Mirror Image | 미러이미징'
    AdvancedDarkSight = 'Advanced Dark Sight | 어드밴스드 다크 사이트'
    LifeDrain = 'Life Drain | 바이탈 스틸'
    EnvelopingDarkness = 'Enveloping Darkness | 래디컬 다크니스'
    ShadowMeld = 'Shadow Meld | 섀도우 이베이젼'
    # Blade Master
    BladeFury = 'Blade Fury | 블레이드 퓨리'
    PhantomBlow = 'Phantom Blow | 팬텀 블로우'
    FinalCut = 'Final Cut | 파이널 컷'
    SuddenRaid = 'Sudden Raid | 써든레이드'
    MirroredTarget = 'Mirrored Target | 더미 이펙트'
    Thorns = 'Thorns | 쏜즈 이펙트'
    Sharpness = 'Sharpness | 샤프니스'
    ToxicVenom = 'Toxic Venom | 페이탈 베놈'
    KataraExpert = 'Katara Expert | 이도류 엑스퍼트'
    # Hypers
    AsurasAnger = 'Asura\'s Anger | 아수라'
    EpicAdventure = 'Epic Adventure | 에픽 어드벤처'
    BladeClone = 'Blade Clone | 히든 블레이드'
    # 5th Job
    BladeTempest = 'Blade Tempest | 블레이드 스톰'
    BladesofDestiny = 'Blades of Destiny | 카르마 퓨리'
    BladeTornado = 'Blade Tornado | 블레이드 토네이도'
    HauntedEdge = 'Haunted Edge | 헌티드 엣지'


class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "LUK2"
        self.jobname = "듀얼블레이드"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=36, armor_ignore=47.7)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        
        Karma = core.InformedCharacterModifier(DualBladeSkills.ChannelKarma.value, att = 30)
        PhisicalTraining = core.InformedCharacterModifier(DualBladeSkills.PhysicalTraining.value, stat_main = 30, stat_sub = 30)
        
        SornsEffect = core.InformedCharacterModifier(DualBladeSkills.Thorns.value, att = 30 + passive_level)
        DualBladeExpert = core.InformedCharacterModifier(DualBladeSkills.KataraExpert.value, att = 30 + passive_level, pdamage_indep = 20 + passive_level // 2)
        Sharpness = core.InformedCharacterModifier(DualBladeSkills.Sharpness.value, crit = 35 + 3 * passive_level, crit_damage = 13 + passive_level)
        ReadyToDiePassive = thieves.ReadyToDiePassiveWrapper(vEhc, 2, 2)
        
        return [Karma, PhisicalTraining, SornsEffect, DualBladeExpert, Sharpness, ReadyToDiePassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 30)
        Mastery = core.InformedCharacterModifier("숙련도", mastery=90+ceil(passive_level / 2))
        return [WeaponConstant, Mastery]

    def get_ruleset(self):
        def check_final_cut_time(final_cut):
            return (final_cut.is_not_usable() and final_cut.is_cooltime_left(80*1000, 1)) # It is more efficient to use only one harrow immediately after breaking. 파컷 직후 써레 1번만 쓰는게 더 효율적임.

        def sync_burst_buff(burst_buff, blade_storm, ultimate_dark_sight):
            if blade_storm.is_usable():
                if ultimate_dark_sight.is_cooltime_left(80000, 1) or ultimate_dark_sight.is_active():
                    return True
            return False

        ruleset = RuleSet()
        ruleset.add_rule(ConditionRule(DualBladeSkills.SuddenRaid.value, DualBladeSkills.FinalCut.value, check_final_cut_time), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(DualBladeSkills.AsurasAnger.value, DualBladeSkills.BladesofDestiny.value, lambda sk: sk.is_cooltime_left(6000, 1)), RuleSet.BASE)  # TODO: Optimized for 4 seconds of cooldown reduction, you need to receive and process cooldown reduction values. 쿨감 4초기준 최적화, 쿨감 수치를 받아와서 처리해야 함.
        ruleset.add_rule(ComplexConditionRule(ThiefSkills.LastResort.value, [DualBladeSkills.BladeTempest.value, ThiefSkills.ShadowWalker.value], sync_burst_buff), RuleSet.BASE)
        ruleset.add_rule(ComplexConditionRule(GlobalSkills.TermsAndConditions.value, [DualBladeSkills.BladeTempest.value, ThiefSkills.ShadowWalker.value], sync_burst_buff), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(DualBladeSkills.BladeTempest.value, ThiefSkills.ShadowWalker.value, lambda sk: sk.is_active() or sk.is_cooltime_left(80000, 1)), RuleSet.BASE)
        ruleset.add_rule(ConditionRule(GlobalSkills.MapleWorldGoddessBlessing.value, ThiefSkills.ShadowWalker.value, lambda sk: sk.is_active() or sk.is_usable()), RuleSet.BASE)
        return ruleset

    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Hyper: Phantom Blow-Reinforce, Ignor Guard, Bonus Attack
        Blade Fury-Reinforce, Extra Target

        Asura 41 strokes
        Blade Tornado 5 Hits

        16 cores valid: Fanble / Asura / Fury - Sudden Raid / Ascension / Hidden Blade

        하이퍼 : 팬텀 블로우 - 리인포스, 이그노어 가드, 보너스 어택
        블레이드 퓨리 - 리인포스, 엑스트라 타겟
        
        아수라 41타
        블레이드 토네이도 5타
        
        코어 16개 유효 : 팬블 / 아수라 / 퓨리 -- 써든레이드 / 어센션 / 히든블레이드
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        #Buff skills
        Booster = core.BuffSkill(DualBladeSkills.KataraBooster.value, 0, 180000, rem = True).wrap(core.BuffSkillWrapper)
        
        DarkSight = core.BuffSkill(DualBladeSkills.DarkSight.value, 0, 1, cooltime = -1).wrap(core.BuffSkillWrapper)#, pdamage_indep = 20 + 10 + int(0.2*vEhc.getV(3,3))).wrap(core.BuffSkillWrapper)
        
        PhantomBlow = core.DamageSkill(DualBladeSkills.PhantomBlow.value, 540, 315 + 3 * self.combat, 6+1, modifier = core.CharacterModifier(armor_ignore = 44, pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        SuddenRaid = core.DamageSkill(DualBladeSkills.SuddenRaid.value, 690, 494+5*self.combat, 7, cooltime = (30-2*(self.combat//2))*1000, red=True).setV(vEhc, 2, 2, False).wrap(core.DamageSkillWrapper)    # Pacutt's remaining cooldown is reduced by 20%. 파컷의 남은 쿨타임 20% 감소.
        SuddenRaidDOT = core.DotSkill(f"{DualBladeSkills.SuddenRaid.value}(DoT | 도트)", 0, 1000, 210 + 4 * self.combat, 1, 10000, cooltime = -1).wrap(core.DotSkillWrapper)
        
        FinalCut = core.DamageSkill(DualBladeSkills.FinalCut.value, 450, 2000 + 20 * self.combat, 1, cooltime = 90000, red=True).wrap(core.DamageSkillWrapper)
        FinalCutBuff = core.BuffSkill(f"{DualBladeSkills.FinalCut.value}(Buff | 버프)", 0, 60000, rem = True, cooltime = -1, pdamage_indep = 40 + self.combat).wrap(core.BuffSkillWrapper)
        
        EpicAdventure = core.BuffSkill(DualBladeSkills.EpicAdventure.value, 0, 60*1000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        FlashBang = core.DamageSkill(DualBladeSkills.Flashbang.value, 390, 250, 1, cooltime = 60000, red=True).wrap(core.DamageSkillWrapper)  # Random delay. 임의 딜레이.
        FlashBangDebuff = core.BuffSkill(f"{DualBladeSkills.Flashbang.value}(Debuff | 디버프)", 0, 50000/2, cooltime = -1, pdamage = 10 * 0.9).wrap(core.BuffSkillWrapper)
        Venom = core.DotSkill(DualBladeSkills.ToxicVenom.value, 0, 1000, 160+5*passive_level, 2+(10+passive_level)//6, 8000, cooltime = -1).wrap(core.DotSkillWrapper)  # Stacks 3 times. 3회 중첩.

        HiddenBladeBuff = core.BuffSkill(f"{DualBladeSkills.BladeClone.value}(Buff | 버프)", 0, 60000, cooltime = 90000, pdamage = 10).wrap(core.BuffSkillWrapper)
        HiddenBlade = core.DamageSkill(DualBladeSkills.BladeClone.value, 0, 140, 1).setV(vEhc, 5, 2, True).wrap(core.DamageSkillWrapper)
        
        Asura = core.DamageSkill(DualBladeSkills.AsurasAnger.value, 810, 0, 0, cooltime = 60000).wrap(core.DamageSkillWrapper)
        AsuraTick = core.DamageSkill(f"{DualBladeSkills.AsurasAnger.value}(Tick | 틱)", 300, 420, 4, modifier =core.CharacterModifier(armor_ignore = 100)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        AsuraEnd = core.DamageSkill(f"{DualBladeSkills.AsurasAnger.value}(Ending | 종료)", 360, 0, 0, cooltime = -1).wrap(core.DamageSkillWrapper)
        
        UltimateDarksight = thieves.UltimateDarkSightWrapper(vEhc, 3, 3, 20)
        ReadyToDie = thieves.ReadyToDieWrapper(vEhc,4,4)
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        BladeStorm = core.DamageSkill(DualBladeSkills.BladeTempest.value, 120, 580+23*vEhc.getV(0,0), 7, red = True, cooltime = 90000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        BladeStormTick = core.DamageSkill(f"{DualBladeSkills.BladeTempest.value}(Tick | 틱)", 210, 350+10*vEhc.getV(0,0), 5, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)  #10000/210 타
        BladeStormEnd = core.DamageSkill(f"{DualBladeSkills.BladeTempest.value}(Ending | 종료)", 120, 0, 0).wrap(core.DamageSkillWrapper)
        
        KarmaFury = core.DamageSkill(DualBladeSkills.BladesofDestiny.value, 750, 400+16*vEhc.getV(1,1), 7 * 5, red = True, cooltime = 10000, modifier = core.CharacterModifier(armor_ignore = 30)).isV(vEhc,1,1).wrap(core.DamageSkillWrapper)
        BladeTornado = core.DamageSkill(DualBladeSkills.BladeTornado.value, 540, 600+24*vEhc.getV(2,2), 7, red = True, cooltime = 12000, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.DamageSkillWrapper)
        BladeTornadoSummon = core.SummonSkill(f"{DualBladeSkills.BladeTornado.value}(Summon | 소환)", 0, 3000/5, 400+16*vEhc.getV(2,2), 6, 3000-1, cooltime=-1, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)
        BladeTornadoSummonMirrorImaging = core.SummonSkill(f"{DualBladeSkills.BladeTornado.value}(Summon | 소환)({DualBladeSkills.MirrorImage.value})", 0, 3000/5, (400+16*vEhc.getV(2,2)) * 0.7, 6, 3000-1, cooltime=-1, modifier = core.CharacterModifier(armor_ignore = 100)).isV(vEhc,2,2).wrap(core.SummonSkillWrapper)

        HauntedEdge = core.DamageSkill(f"{DualBladeSkills.HauntedEdge.value}(Yaksa | 나찰)", 0, 200+8*vEhc.getV(0,0), 4*5, cooltime=14000, red=True, modifier=core.CharacterModifier(armor_ignore=30)).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
    
        SuddenRaid.onAfter(SuddenRaidDOT)
        FinalCut.onAfter(FinalCutBuff)
        
        HiddenBladeOpt = core.OptionalElement(HiddenBladeBuff.is_active, HiddenBlade)
        
        FlashBang.onAfter(FlashBangDebuff)
        for sk in [FinalCut, PhantomBlow, SuddenRaid, FlashBang, AsuraTick, BladeStorm, BladeStormTick, BladeTornado, KarmaFury]:
            sk.onAfter(HiddenBladeOpt)
            
        for sk in [PhantomBlow, AsuraTick, BladeStormTick]:
            sk.onAfter(Venom)
        
        AsuraRepeat = core.RepeatElement(AsuraTick, 26)  # Up to 28 times are possible, but 26 times are set for dpm optimization. 최대 28회까지 가능하나, dpm 최적화를 위해 26회로 설정함.
        Asura.onAfter(AsuraRepeat)
        AsuraRepeat.onAfter(AsuraEnd)

        BladeStormRepeat = core.RepeatElement(BladeStormTick, 48)
        BladeStorm.onAfter(BladeStormRepeat)
        BladeStormRepeat.onAfter(BladeStormEnd)

        BladeTornado.onAfter(BladeTornadoSummon)
        BladeTornado.onAfter(BladeTornadoSummonMirrorImaging)

        SuddenRaid.onAfter(FinalCut.controller(0.2, "reduce_cooltime_p"))

        PhantomBlow.onAfter(core.OptionalElement(HauntedEdge.is_available, HauntedEdge, name="Haunted Edge cooldown check | 헌티드 엣지 쿨타임 체크"))
        HauntedEdge.protect_from_running()

        for sk in [PhantomBlow, SuddenRaid, FinalCut, FlashBang, AsuraTick, 
            BladeStorm, BladeStormTick, KarmaFury, BladeTornado, HiddenBlade, HauntedEdge]:
            jobutils.create_auxilary_attack(sk, 0.7, nametag=f'({DualBladeSkills.MirrorImage.value})')
        
        return(PhantomBlow,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(),
                    Booster, DarkSight, FinalCutBuff, EpicAdventure, FlashBangDebuff, HiddenBladeBuff, globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat),
                    UltimateDarksight, ReadyToDie, globalSkill.soul_contract()] +\
                [FinalCut, FlashBang, BladeTornado, SuddenRaid, KarmaFury, BladeStorm, Asura, MirrorBreak, MirrorSpider] +\
                [SuddenRaidDOT, Venom, BladeTornadoSummon, BladeTornadoSummonMirrorImaging, HauntedEdge] +\
                [] +\
                [PhantomBlow])