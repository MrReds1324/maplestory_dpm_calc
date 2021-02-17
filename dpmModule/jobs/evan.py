from enum import Enum

from ..kernel.graph import DynamicVariableOperation
from ..kernel import core
from ..kernel.core import CharacterModifier as MDF
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from . import globalSkill
from .jobclass import heroes
from .jobbranch import magicians
from typing import Any, Dict


# English skill information for Evan here https://maplestory.fandom.com/wiki/Evan/Skills
class EvanSkills(Enum):
    # Link Skill
    RunePersistence = 'Rune Persistence | 룬 퍼시스턴스'
    # Beginner
    InheritedWill = 'Inherited Will | 계승된 의지'
    # 1st Job
    ManaBurstI = 'Mana Burst I | 서클 오브 마나Ⅰ'
    Teleport = 'Teleport | 텔레포트'
    MagicGuard = 'Magic Guard | 매직 가드'
    DragonSoul = 'Dragon Soul | 드래곤 소울'
    MagicLink = 'Magic Link | 링크드 매직'
    DragonSpark = 'Dragon Spark | 드래곤 스파킹'
    # 2nd Job
    ManaBurstII = 'Mana Burst II | 서클 오브 마나II'
    WindCircle = 'Wind Circle | 서클 오브 윈드'
    DragonFlash = 'Dragon Flash | 드래곤 스위프트'
    WindFlash = 'Wind Flash | 스위프트 오브 윈드'
    ReturnFlash = 'Return Flash | 스위프트-돌아와!'
    Return = 'Return! | 돌아와!'
    MagicBooster = 'Magic Booster | 매직 부스터'
    SupportJump = 'Support Jump | 서포트 점프'
    HighWisdom = 'High Wisdom | 하이 위즈덤'
    Partners = 'Partners | 교감'
    SpellMastery = 'Spell Mastery | 스펠 마스터리'
    AdvancedDragonSpark = 'Advanced Dragon Spark | 어드밴스 드래곤 스파킹'
    # 3rd Job
    ManaBurstIII = 'Mana Burst III | 서클 오브 마나III'
    ThunderCircle = 'Thunder Circle | 서클 오브 썬더'
    DragonDive = 'Dragon Dive | 드래곤 다이브'
    ReturnDive = 'Return Dive | 다이브-돌아와!'
    ThunderDive = 'Thunder Dive | 다이브 오브 썬더'
    ThunderFlash = 'Thunder Flash | 스위프트 오브 썬더'
    MagicDebris = 'Magic Debris | 마법 잔해'
    ElementalDecrease = 'Elemental Decrease | 엘리멘탈 리셋'
    CriticalMagic = 'Critical Magic | 크리티컬 매직'
    MagicResistance = 'Magic Resistance | 매직 레지스턴스'
    MagicAmplification = 'Magic Amplification | 매직 엠플리피케이션'
    DragonPotential = 'Dragon Potential | 드래곤 포텐셜'
    # 4th Job
    ManaBurstIV = 'Mana Burst IV | 서클 오브 마나IV'
    EarthCircle = 'Earth Circle | 서클 오브 어스'
    DragonBreath = 'Dragon Breath | 드래곤 브레스'
    WindBreath = 'Wind Breath | 브레스 오브 윈드'
    EarthBreath = 'Earth Breath | 브레스 오브 어스'
    ReturnFlame = 'Return Flame | 브레스-돌아와!'
    EarthDive = 'Earth Dive | 다이브 오브 어스'
    DarkFog = 'Dark Fog | 다크 포그'
    BlessingoftheOnyx = 'Blessing of the Onyx | 오닉스의 축복'
    EnhancedMagicDebris = 'Enhanced Magic Debris | 강화된 마법 잔해'
    MagicMastery = 'Magic Mastery | 매직 마스터리'
    OnyxWill = 'Onyx Will | 오닉스의 의지'
    DragonFury = 'Dragon Fury | 드래곤 퓨리'
    HighDragonPotential = 'High Dragon Potential | 하이 드래곤 포텐셜'
    # Hypers
    DragonMaster = 'Dragon Master | 드래곤 마스터'
    SummonOnyxDragon = 'Summon Onyx Dragon | 서먼 오닉스 드래곤'
    HeroicMemories = 'Heroic Memories | 히어로즈 오쓰'
    # 5th Job
    ElementalBarrage = 'Elemental Barrage | 엘리멘탈 블래스트'
    DragonSlam = 'Dragon Slam | 드래곤 브레이크'
    WyrmkingsBreath = 'Wyrmking\'s Breath | 임페리얼 브레스'
    LudicrousSpeed = 'Ludicrous Speed | 드래곤 브레이크-돌아와!'
    ElementalRadiance = 'Elemental Radiance | 조디악 레이'
    SpiralofMana = 'Spiral of Mana | 스파이럴 오브 마나'


class MagicParticleWrapper(core.DamageSkillWrapper):
    def __init__(self, vEhc, upgrade_index, passive_level):
        skill = core.DamageSkill(EvanSkills.MagicDebris.value, 0, 110, 1).setV(vEhc, upgrade_index, 2, True)
        super(MagicParticleWrapper, self).__init__(skill)
        self.stack = 0
        self.passive_level = passive_level
        self.stackCooltimeLeft = 0

    def spend_time(self, time):
        self.stackCooltimeLeft -= time
        super(MagicParticleWrapper, self).spend_time(time)

    def _add_stack(self):
        if self.stackCooltimeLeft <= 0:
            self.stack += 1
            self.stackCooltimeLeft = 400
        return self._result_object_cache

    def add_stack(self):
        task = core.Task(self, self._add_stack)
        return core.TaskHolder(task, name=f"{EvanSkills.MagicDebris.value}(Add | 추가)")

    def _use(self, skill_modifier):
        result = super(MagicParticleWrapper, self)._use(skill_modifier)
        self.stack = 0
        return result

    def get_damage(self):
        return self.skill.damage + 2*self.passive_level + (100 + self.passive_level) * (self.stack // 5)

    def get_hit(self):
        return self.skill.hit * self.stack

    def is_usable(self):
        return self.stack >= 15

class ZodiacRayWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        skill = core.SummonSkill(EvanSkills.ElementalRadiance.value, 780, 180, 400+16*vEhc.getV(num1,num2), 6, (14+vEhc.getV(num1,num2)//10)*1000+240, cooltime = 180*1000, red=True, modifier = MDF(armor_ignore = 100)).isV(vEhc,num1,num2)
        self.mana = 0
        self.open = False
        super(ZodiacRayWrapper, self).__init__(skill)
    
    def _use(self, skill_modifier):
        result = super(ZodiacRayWrapper, self)._use(skill_modifier)
        self.mana = 0
        self.open = False
        self.tick = 99999999
        return result
    
    def _add_mana(self, count):
        self.mana += count
        if self.mana >= 25 and self.open == False:
            self.open = True
            self.tick = 1800
        return self._result_object_cache

    def add_mana(self, count):
        task = core.Task(self, partial(self._add_mana, count))
        return core.TaskHolder(task, name=f"Magic Attack | 마력{count:+d}")

class SpiralOfManaWrapper(core.SummonSkillWrapper):
    def __init__(self, vEhc, num1, num2):
        self.penaltyTime = 0
        skill = core.SummonSkill(
            EvanSkills.SpiralofMana.value, 360, 420, 235+vEhc.getV(num1,num2), 6, 7000, cooltime=5000-50*vEhc.getV(num1,num2), red=True
        ).setV(vEhc, 0, 2, False).isV(vEhc, num1, num2)
        super(SpiralOfManaWrapper, self).__init__(skill)

    def spend_time(self, time):
        self.penaltyTime -= time
        super(SpiralOfManaWrapper, self).spend_time(time)

    def _use(self, skill_modifier):
        result = super(SpiralOfManaWrapper, self)._use(skill_modifier)
        self.tick = 780 # TODO: Enable to input attack start time in SummonSkill. SummonSkill에 공격 시작 시간 입력 가능하게 할 것.
        self.penaltyTime = 0
        return result

    def _setPenalty(self):
        if self.is_active():
            self.penaltyTime = 1000
        return self._result_object_cache

    def setPenalty(self):
        task = core.Task(self, self._setPenalty)
        return core.TaskHolder(task, name="Mana Burst reduction | 스오마 타수 감소")

    def get_hit(self): # 서오마 사용후 1초간 3타, 미사용시 6타
        if self.penaltyTime > 0:
            return self.skill.hit - 3
        else:
            return self.skill.hit

class MirSkillWrapper(core.SummonSkillWrapper):
    def __init__(self, skill):
        super(MirSkillWrapper, self).__init__(skill)
        self.attacking = False

    def _use(self, skill_modifier):
        self.attacking = True
        return super(MirSkillWrapper, self)._use(skill_modifier)

    def endSoon(self, time):
        """
        When the fusion/return cast is judged by only available and timeLeft, the activation often fails because available first becomes false.
        With the attacking variable set aside, it is determined whether the skill can be cast by fusion/return under the premise that the skill is terminated only by always fusion/return.

        available, timeLeft만으로 융합/돌아와 시전을 판정하면 종종 available이 먼저 false가 되어 발동에 실패함.
        attacking 변수를 따로 두고, 항상 융합/돌아와 만으로만 스킬이 종료된다는 전제 하에 융합/돌아와 시전 가능 여부를 판정함.
        """
        return self.attacking and self.timeLeft <= time

    def _end(self):
        self.timeLeft = 0
        self.attacking = False
        return self._result_object_cache

    def end(self):
        task = core.Task(self, self._end)
        return core.TaskHolder(task, name="Ending | 종료")

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.jobtype = "INT"
        self.jobname = "에반"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'reuse', 'buff_rem')
        self.preEmptiveSkills = 1

    def get_modifier_optimization_hint(self):
        return core.CharacterModifier(pdamage=24, armor_ignore=5)

    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        InheritWill = core.InformedCharacterModifier(EvanSkills.InheritedWill.value,att = 10, stat_main = 10, stat_sub = 10)
        LinkedMagic = core.InformedCharacterModifier(EvanSkills.MagicLink.value,att = 20)
        
        HighWisdom =  core.InformedCharacterModifier(EvanSkills.HighWisdom.value,stat_main = 40)

        SpellMastery = core.InformedCharacterModifier(EvanSkills.SpellMastery.value,crit = 15, att = 10)
        
        ElementalReset = core.InformedCharacterModifier(EvanSkills.ElementalDecrease.value,pdamage_indep = 15)
        CriticalMagic = core.InformedCharacterModifier(EvanSkills.CriticalMagic.value,crit = 30, crit_damage = 20)
        MagicAmplification = core.InformedCharacterModifier(EvanSkills.MagicAmplification.value,pdamage_indep = 30)
        DragonPotential = core.InformedCharacterModifier(EvanSkills.DragonPotential.value,armor_ignore = 20)
        
        MagicMastery = core.InformedCharacterModifier(EvanSkills.MagicMastery.value,att = 30 + passive_level, crit_damage = 20 + passive_level//2)
        DragonFury = core.InformedCharacterModifier(EvanSkills.DragonFury.value,patt = 35 + passive_level)
        HighDragonPotential = core.InformedCharacterModifier(EvanSkills.HighDragonPotential.value,boss_pdamage = 20+passive_level)

        SpiralOfManaPassive = core.InformedCharacterModifier(f"{EvanSkills.SpiralofMana.value}(Passive | 패시브)", att=5+vEhc.getV(0,0))
        
        return [InheritWill, LinkedMagic,
            HighWisdom, SpellMastery, ElementalReset, CriticalMagic, MagicAmplification, DragonPotential,
            MagicMastery, DragonFury, HighDragonPotential, SpiralOfManaPassive]

    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        passive_level = chtr.get_base_modifier().passive_level + self.combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 0)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -2.5 + 0.5*passive_level)  
        Interaction = core.InformedCharacterModifier(EvanSkills.Partners.value,pdamage = 20)
        ElementalResetActive = core.InformedCharacterModifier(f"{EvanSkills.ElementalDecrease.value}(Use | 사용)", prop_ignore = 10)
        
        return [WeaponConstant, Mastery, Interaction, ElementalResetActive]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, options: Dict[str, Any]):
        '''
        Dao-Breath-Bore

        Dao 3 hits

        Hyper:
        Des / Deda / Deve Cool Reduce
        Deda-Earth Enhance
        Dev-Wind Bonus Chance

        All fusion skills are canceled except for the 5th

        Core strengthening
        Seooma, Seoeo (+ Dao, Beo), Breath (Breath-Come back), Seoowin, (+ Bowin, Seowin)
        Seo Sun (Seo Sun, Dao Sun), Dragon Master, Magic Wreck, Dragon Sparking, Swift

        다오어-브레스-브오어

        다오어 3히트
        
        하이퍼 : 
        드스 / 드다 / 드브 쿨리듀스
        드다 - 어스 인핸스
        드브 - 윈드 보너스 찬스
        
        모든 융합스킬은 5차를 제외하고 전부 캔슬
        
        코어 강화
        서오마, 서오어 (+ 다오어, 브오어), 브레스(브레스-돌아와), 서오윈,(+ 브오윈, 스오윈)
        서오썬(스오썬, 다오썬), 드래곤 마스터, 마법 잔해, 드래곤 스파킹, 스위프트
        '''
        passive_level = chtr.get_base_modifier().passive_level + self.combat
        SWIFT_OF_THUNDER_HIT = 2
        DIVE_OF_EARTH_HIT = 3
        BREAK_BACK_HIT_RATE = 0
        BREATH_OF_WIND_BONUS = options.get("hp_rate", False)

        ######   Skill   ######
        #Buff skills
        Booster = core.BuffSkill(EvanSkills.MagicBooster.value, 0, 180 * 1000, rem = True).wrap(core.BuffSkillWrapper)
        OnixBless = core.BuffSkill(EvanSkills.BlessingoftheOnyx.value, 0, (180+2*self.combat)*1000, rem = True, att = 80+2*self.combat).wrap(core.BuffSkillWrapper)

        ### Fusion skill. 에반 스킬.
        CircleOfMana1 = core.DamageSkill(f"{EvanSkills.ManaBurstIV.value}(1st hit | 1타)", 180, 290 + self.combat, 4).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfMana2 = core.DamageSkill(f"{EvanSkills.ManaBurstIV.value}(2nd hit | 2타)", 390, 330 + self.combat, 4).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        DragonSparking = core.DamageSkill(EvanSkills.DragonSpark.value, 0, 150, 1).setV(vEhc, 7, 3, True).wrap(core.DamageSkillWrapper)
        MagicParticle = MagicParticleWrapper(vEhc, 6, passive_level)
        
        CircleOfWind = core.DamageSkill(EvanSkills.WindCircle.value, 660, 320+self.combat, 5).setV(vEhc, 3, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfThunder = core.DamageSkill(EvanSkills.ThunderCircle.value, 660, 320+self.combat, 5).setV(vEhc, 4, 2, False).wrap(core.DamageSkillWrapper)
        CircleOfEarth = core.DamageSkill(EvanSkills.EarthCircle.value, 660, 320+self.combat, 5).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper)
        DarkFog = core.DamageSkill(EvanSkills.DarkFog.value, 870, 400+2*self.combat, 6, cooltime = 40000, red=True).wrap(core.DamageSkillWrapper)
        
        ### Mir skill. 미르 스킬.
        Mir = core.BuffSkill("Mir | 미르(Attacking | 공격중)", 0, 0, cooltime=-1).wrap(core.BuffSkillWrapper)
        DragonSwift = core.SummonSkill(EvanSkills.DragonFlash.value, 0, 540, 415 + 2*self.combat, 4, 3360, cooltime = 6000, red=True).setV(vEhc, 8, 2, False).wrap(MirSkillWrapper)
        DragonDive = core.SummonSkill(EvanSkills.DragonDive.value, 0, 360, 325 + self.combat, 3, 3480, cooltime = 6000, red=True).wrap(MirSkillWrapper)
        DragonBreath = core.SummonSkill(EvanSkills.DragonBreath.value, 0, 360, 240 + self.combat, 5, 2880, cooltime = 7500, red=True).setV(vEhc, 2, 2, False).wrap(MirSkillWrapper)

        ## Fusion skill. 융합 스킬.
        SwiftOfWind = core.SummonSkill(EvanSkills.WindFlash.value, 0, 360, 215 + self.combat, 2*3, 3360, cooltime=-1, modifier=MDF(pdamage_indep=-35)).setV(vEhc, 3, 2, False).wrap(MirSkillWrapper)
        SwiftOfThunder = core.SummonSkill(EvanSkills.ThunderFlash.value, 0, 2280/SWIFT_OF_THUNDER_HIT, 450 + self.combat, 6, 2280, cooltime=-1).setV(vEhc, 4, 2, False).wrap(MirSkillWrapper)
        # DiveOfThunder - 안씀.
        DiveOfEarth = core.SummonSkill(EvanSkills.EarthDive.value, 0, 2310/DIVE_OF_EARTH_HIT, 190 + 420, 6, 2310, cooltime=-1, modifier = MDF(pdamage = 20)).setV(vEhc, 1, 2, False).wrap(MirSkillWrapper) # 컴뱃오더스: 위컴알 기준 적용이나 인게임에서 미적용
        BreathOfWind = core.SummonSkill(EvanSkills.WindBreath.value, 0, 450, 215+self.combat+BREATH_OF_WIND_BONUS*(65+self.combat+85), 5, 3510, cooltime=-1).setV(vEhc, 3, 2, False).wrap(MirSkillWrapper)
        BreathOfEarth = core.SummonSkill(EvanSkills.EarthBreath.value, 0, 450, 280+self.combat, 5, 3510, cooltime=-1).setV(vEhc, 1, 2, False).wrap(MirSkillWrapper)
        
        ### Come back! 돌아와!
        SwiftBack = core.BuffSkill(EvanSkills.ReturnFlash.value, 30, 60000, cooltime=-1, pdamage_indep = 10).wrap(core.BuffSkillWrapper)
        DiveBack = core.BuffSkill(EvanSkills.ReturnDive.value, 30, 60000, cooltime=-1, rem=True).wrap(core.BuffSkillWrapper)
        BreathBack = core.SummonSkill(EvanSkills.ReturnFlame.value, 30, 450, 150+self.combat, 1, (30+self.combat // 2)*1000, cooltime=-1).setV(vEhc, 2, 2, False).wrap(core.SummonSkillWrapper)
        
        # Hyper. 하이퍼.
        SummonOnixDragon = core.SummonSkill(EvanSkills.SummonOnyxDragon.value, 900, 3030, 550, 2, 40000, cooltime = 80000).wrap(core.SummonSkillWrapper)
        
        # Dragon Master-Unused. 드래곤 마스터 - 미사용.
        HerosOath = core.BuffSkill(EvanSkills.HeroicMemories.value, 0, 60000, cooltime = 120 * 1000, pdamage = 10).wrap(core.BuffSkillWrapper)
        
        # 5th. 5차.
        MirrorBreak, MirrorSpider = globalSkill.SpiderInMirrorBuilder(vEhc, 0, 0)
        
        # The final damage stack is applied for each hit. 1 stroke (0%) -2 stroke (5%) -3 stroke (10%) -4 stroke (15%) = 7.5% average. 각 타마다 최종뎀 스택이 적용됨. 1타(0%)-2타(5%)-3타(10%)-4타(15%) = 평균 7.5%.
        ElementalBlast = core.DamageSkill(EvanSkills.ElementalBarrage.value, 600, 750+30*vEhc.getV(2,3), 6 * 4, cooltime = 60000, red = True, modifier = MDF(crit = 100, pdamage_indep = 7.5)).isV(vEhc,2,3).wrap(core.DamageSkillWrapper)
        ElementalBlastBuff = core.BuffSkill(f"{EvanSkills.ElementalBarrage.value}(Buff | 버프)", 0, 10000, pdamage_indep = 20, cooltime=-1).isV(vEhc,2,3).wrap(core.BuffSkillWrapper)

        DragonBreak = core.SummonSkill(EvanSkills.DragonSlam.value, 0, 360, 450+18*vEhc.getV(5,5), 7, 2500, cooltime = 20000, red=True).isV(vEhc,5,5).wrap(MirSkillWrapper)
        DragonBreakBack = core.SummonSkill(EvanSkills.LudicrousSpeed.value, 30, 510, 150+6*vEhc.getV(5,5), 3 * BREAK_BACK_HIT_RATE, 5000, cooltime=-1).isV(vEhc,5,5).wrap(core.SummonSkillWrapper)
        ImperialBreath = core.SummonSkill(EvanSkills.WyrmkingsBreath.value, 0, 240, 500+20*vEhc.getV(5,5), 7, 4000, cooltime=-1).isV(vEhc,5,5).wrap(MirSkillWrapper)

        ZodiacRay = ZodiacRayWrapper(vEhc, 4, 2)

        SpiralOfMana = SpiralOfManaWrapper(vEhc, 0, 0)
        
        ##### build graph #####
        CircleOfMana1.onAfter(SpiralOfMana.setPenalty())
        CircleOfMana1.onAfter(core.OptionalElement(SpiralOfMana.is_not_active, SpiralOfMana, CircleOfMana2))
        SpiralOfMana.protect_from_running()

        # Magic wreckage. 마법 잔해.
        AddParticle = MagicParticle.add_stack()
        BreathOfEarth.onTick(AddParticle)
        BreathOfWind.onTick(AddParticle)
        DiveOfEarth.onTick(AddParticle)
        SwiftOfThunder.onTick(AddParticle)
        SwiftOfWind.onTick(AddParticle)
        
        # Mir constraint. 미르 제한조건.
        MirConstraint = core.ConstraintElement("Mir | 미르(In use | 사용중)", Mir, Mir.is_not_active)

        for sk in [DragonSwift, DragonDive, DragonBreath, DragonBreak]:
            sk.onConstraint(MirConstraint)
            sk.onAfter(Mir.controller(DynamicVariableOperation.reveal_argument(sk.skill.remain), "set_enabled_and_time_left"))

        for sk in [BreathOfEarth, BreathOfWind, DiveOfEarth, ImperialBreath]:
            sk.onAfter(Mir.controller(DynamicVariableOperation.reveal_argument(sk.skill.remain), "set_enabled_and_time_left"))

        for back, li in [(SwiftBack, [DragonSwift, SwiftOfThunder, SwiftOfWind]), (DiveBack, [DragonDive, DiveOfEarth]),
                    (BreathBack, [DragonBreath, BreathOfEarth, BreathOfWind]), (DragonBreakBack, [DragonBreak, ImperialBreath])]:
            for sk in li:
                back.onAfter(sk.end())
            back.onAfter(Mir.controller(1))

        # Brake/Elble/Imb. 브레이크/엘블/임브.
        ElementalBlast.onConstraint(core.ConstraintElement(f"{EvanSkills.ElementalBarrage.value}(Execution condition | 실행조건)", Mir, lambda: DragonBreak.endSoon(1000)))
        ElementalBlast.onAfter(ElementalBlastBuff)
        ElementalBlast.onAfter(ImperialBreath)
        
        ImperialBreath.onAfter(DragonBreak.end())

        DragonBreak.onAfter(DragonBreakBack.controller(1))
        ImperialBreath.onAfter(DragonBreakBack.controller(1))
        DragonBreakBack.onConstraint(core.ConstraintElement(f"{EvanSkills.LudicrousSpeed.value}(Execution condition | 실행조건)", Mir,
            lambda: ImperialBreath.endSoon(1000) or (DragonBreak.endSoon(1000) and not ElementalBlast.is_available())
        ))

        # Breath. 브레스.
        DragonBreath.onAfter(BreathOfEarth.controller(1))
        BreathOfEarth.onConstraint(core.ConstraintElement("브오어 (Execution condition | 실행조건)", Mir, lambda: DragonBreath.endSoon(1000)))
        BreathOfEarth.onAfter(CircleOfMana1)  # 마나캔슬.
        BreathOfEarth.onAfter(DragonBreath.end())
        
        BreathOfEarth.onAfter(BreathBack.controller(1))
        BreathBack.onConstraint(core.ConstraintElement(f"{EvanSkills.ReturnFlame.value}(Execution condition | 실행조건)", Mir, lambda: BreathOfEarth.endSoon(1000)))

        # Dive. 다이브.
        DragonDive.onAfter(DiveOfEarth.controller(1))
        DiveOfEarth.onConstraint(core.ConstraintElement("다오어 실행조건", Mir, lambda: DragonDive.is_active()))
        DiveOfEarth.onAfter(CircleOfMana1)  # 마나캔슬.
        DiveOfEarth.onAfter(DragonDive.end())

        DiveOfEarth.onAfter(core.OptionalElement(lambda: DiveBack.is_time_left(8500, -1), DiveBack.controller(1)))
        DiveBack.onConstraint(core.ConstraintElement(f"{EvanSkills.ReturnDive.value}(Execution condition | 실행조건)", Mir, lambda: DiveOfEarth.endSoon(1000)))

        # Swift. 스위프트.
        DragonSwift.onConstraint(core.ConstraintElement("스위프트 실행조건", Mir, lambda: SwiftBack.is_time_left(5000, -1))) # 버프 없을때만 사용
        SwiftOfWind.onAfter(DragonSwift.end())

        DragonSwift.onAfter(SwiftBack.controller(1))
        SwiftOfWind.onAfter(SwiftBack.controller(1))
        SwiftBack.onConstraint(core.ConstraintElement(f"{EvanSkills.ReturnFlash.value}(Execution condition | 실행조건)", Mir, lambda: SwiftOfWind.is_active() or DragonSwift.is_active())) # 스위프트 즉시 종료

        # Swift Zodiac Ray. 조디악 레이.
        ZodiacStack3 = ZodiacRay.add_mana(3)
        ZodiacStack1 = ZodiacRay.add_mana(1)
        for sk in [DragonBreath, CircleOfWind, BreathOfWind, BreathBack, CircleOfEarth, SwiftOfWind, DarkFog]:
            sk.onJustAfter(ZodiacStack3)
        for sk in [MagicParticle, DragonSwift]:
            sk.onJustAfter(ZodiacStack1)
        for sk in [MagicParticle, DragonBreath, CircleOfWind, BreathOfWind, BreathBack, MagicParticle, DragonSwift, CircleOfEarth, SwiftOfWind, MagicParticle, DarkFog]:
            ZodiacRay.onAfter(sk)
        
        # Final Attack. 파이널 어택.
        for i in [CircleOfMana2, CircleOfEarth, CircleOfWind, CircleOfThunder, DarkFog]:
            i.onAfter(DragonSparking)

        # Overload mana. 오버로드 마나.
        overload_mana_builder = magicians.OverloadManaBuilder(vEhc, 1, 2)
        for sk in [CircleOfMana1, CircleOfMana2, CircleOfEarth, CircleOfThunder, CircleOfWind, DarkFog, ElementalBlast, SpiralOfMana,
                    DragonSwift, SwiftOfWind, SwiftOfThunder, DragonDive, DiveOfEarth, DragonBreath, BreathOfWind, BreathOfEarth,
                    DragonBreath, ImperialBreath]:
            overload_mana_builder.add_skill(sk)
        OverloadMana = overload_mana_builder.get_buff()
            
        return(CircleOfMana1,
                [globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                    Mir, OverloadMana, Booster, OnixBless, HerosOath, ElementalBlastBuff,
                    globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [ZodiacRay, MagicParticle] +\
                [SummonOnixDragon, SpiralOfMana, DragonBreak, DragonBreakBack, ElementalBlast, ImperialBreath,
                    DragonSwift, SwiftBack, DragonDive, DiveOfEarth, DiveBack, DragonBreath, BreathOfEarth, BreathBack, MirrorBreak, MirrorSpider] +\
                [] +\
                [CircleOfMana1])