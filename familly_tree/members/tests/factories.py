import factory

from members.models import Member


class MemberFactory(factory.Factory):
    class Meta:
        model = Member

    firstname = factory.Faker("first_name")
    lastname = factory.Faker("last_name")
    family_name = factory.LazyAttribute(lambda obj: obj.lastname)
    sex = factory.Iterator([Member.Sex.MALE, Member.Sex.FEMALE])
    birth_date = None
    death_date = None
    father = None
    mother = None
    description = None

    @classmethod
    def build_man(cls, **kwargs):
        return MemberFactory.build(sex="m", **kwargs)

    @classmethod
    def build_woman(cls, **kwargs):
        return super().build(sex="f", **kwargs)


def create_and_save_man(**kwargs) -> Member:
    member = MemberFactory.build_man(**kwargs)
    member.save()
    return member


def create_and_save_woman(**kwargs) -> Member:
    member = MemberFactory.build_woman(**kwargs)
    member.save()
    return member


def create_and_save_member(**kwargs) -> Member:
    member = MemberFactory.build(**kwargs)
    member.save()
    return member
