import datetime
import re

from django.contrib.localflavor.us.us_states import US_STATES
from django.db import models
from django.template.defaultfilters import slugify

EARLIEST_START_DATE = '1995-01-03'
AP_STATES = {'AK': 'Alaska', 'AL': 'Ala.', 'AR': 'Ark.', 'AS': 'A.S.', 'AZ': 'Ariz.', 'CA': 'Calif.', 'CO': 'Colo.', 'CT': 'Conn.', 'DC': 'D.C.',
             'DE': 'Del.', 'FL': 'Fla.', 'GA': 'Ga.', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Ill.', 'IN': 'Ind.',
             'KS': 'Kan.', 'KY': 'Ky.', 'LA': 'La.', 'MA': 'Mass.', 'MD': 'Md.', 'ME': 'Maine', 'MI': 'Mich.', 'MN': 'Minn.', 'MO': 'Mo.',
             'MP': 'M.P.', 'MS': 'Miss.', 'MT': 'Mont.', 'NC': 'N.C.', 'ND': 'N.D.', 'NE': 'Neb.', 'NH': 'N.H.', 'NJ': 'N.J.', 'NM': 'N.M.',
             'NV': 'Nev.', 'NY': 'N.Y.', 'OH': 'Ohio', 'OK': 'Okla.', 'OR': 'Ore.', 'PA': 'Pa.', 'PR': 'P.R.', 'RI': 'R.I.', 'SC': 'S.C.',
             'SD': 'S.D.', 'TN': 'Tenn.', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Va.', 'VI': 'V.I.', 'VT': 'Vt.', 'WA': 'Wash.', 'WI': 'Wis.',
             'WV': 'W.Va.', 'WY': 'Wyo.', }
PARTIES = {'D': 'Democrat',
           'R': 'Republican',
           'ID': 'Independent Democrat',
           'I': 'Independent', }
TITLE_ABBREVS = {'Representative': 'Rep.',
                 'Senator': 'Sen.',
                 'Delegate':, 'Del.', }


class Member(models.Model):
    """A Legislator in congress, linked to many MemberRoles
    """
    bioguide_id = models.CharField(max_length=7, primary_key=True)
    govtrack_id = models.CharField(max_length=10, db_index=True)
    prefix = models.CharField(max_length=16)
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64, db_index=True)
    suffix = models.CharField(max_length=16)
    birth_death = models.CharField(max_length=16)
    position = models.CharField(max_length=24, db_index=True)
    party = models.CharField(max_length=32, db_index=True)
    state = models.CharField(max_length=2, db_index=True)
    district = models.CharField(max_length=3, db_index=True)
    congress = models.CharField(max_length=3, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-congress', 'bioguide_id')

    def __unicode__(self):
        return ' '.join([self.prefix, self.first, self.last, self.suffix, ])

    def slug(self):
        return slugify(self.name())[:50]

    def name(self):
        return re.sub(r'\s\s+', ' ', '%s %s %s' % (self.first, self.middle, self.last))

    def verbose_party(self):
        return PARTIES.get(self.party, self.party)

    def verbose_state(self):
        return dict(US_STATES).get(self.state, self.state)

    def honorific(self):
        TITLE_ABBREVS.get(self.title, self.title)

    def is_sitting(self):
        return len(self.roles.current()) > 0


class MemberRoleManager(models.Manager):
    def current(qset):
        return qset.filter(begin_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())


class MemberRole(models.Model):
    """A single role in which a congressmember served. Fields are duplicative
       of Member, but are a historical record rather than the current state.
       Multiple roles may belong to a single congress.
    """
    member = models.ForeignKey('Member', related_name='roles', db_index=True)
    bioguide_id = models.CharField(max_length=7, db_index=True, help_text="The Bioguide id this member had during this role.")
    begin_date = models.DateField(help_text="The date this role started")
    end_date = models.DateField(help_text="The date this role ended")
    prefix = models.CharField(max_length=16)
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64, db_index=True)
    suffix = models.CharField(max_length=16)
    position = models.CharField(max_length=24, db_index=True)
    party = models.CharField(max_length=32, db_index=True)
    state = models.CharField(max_length=2, db_index=True)
    district = models.CharField(max_length=3, db_index=True)
    congress = models.CharField(max_length=3, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MemberRoleManager()

    class Meta:
        unique_together = (('bioguide_id', 'begin_date', ))
        ordering = ('-start_date', 'member__bioguide_id')

    def __unicode__(self):
        return ' '.join([self.prefix, self.first, self.last, self.suffix, ])

    def slug(self):
        return slugify(self.name())[:50]

    def name(self):
        return re.sub(r'\s\s+', ' ', '%s %s %s' % (self.first, self.middle, self.last))

    def verbose_party(self):
        return PARTIES.get(self.party, self.party)

    def verbose_state(self):
        return dict(US_STATES).get(self.state, self.state)

    def honorific(self):
        TITLE_ABBREVS.get(self.title, self.title)


"""The below models are deprecated, but still used in production while I monitor those above"""

class Legislator(models.Model):
    """Model representing a legislator in a session of congress.
    """
    bioguide_id = models.CharField(max_length=7, db_index=True)
    prefix = models.CharField(max_length=16)
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    suffix = models.CharField(max_length=16)
    birth_death = models.CharField(max_length=16)
    position = models.CharField(max_length=24)
    party = models.CharField(max_length=32)
    state = models.CharField(max_length=2)
    congress = models.CharField(max_length=3)

    class Meta:
        unique_together = (('bioguide_id', 'congress', 'position', ))

    def __unicode__(self):
        return ' '.join([self.prefix, self.first, self.last, self.suffix, ])


class LegislatorRole(models.Model):
    bioguide_id = models.CharField(max_length=7, db_index=True)
    first = models.CharField(max_length=64)
    middle = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    congress = models.IntegerField()
    chamber = models.CharField(max_length=16)
    party = models.CharField(max_length=5)
    title = models.CharField(max_length=64)
    state = models.CharField(max_length=2)
    district = models.CharField(max_length=3)
    begin_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = (('bioguide_id', 'begin_date', 'end_date', ))

    def __unicode__(self):
        return '%s, %s %s' % (self.last, self.first, self.middle)

    def slug(self):
        return slugify(self.name())[:50]

    def name(self):
        return re.sub(r'\s\s+', ' ', '%s %s %s' % (self.first, self.middle, self.last))

    def verbose_party(self):
        return PARTIES.get(self.party, self.party)

    def verbose_state(self):
        return dict(US_STATES).get(self.state, self.state)

    def honorific(self):
        TITLE_ABBREVS.get(self.title, self.title)

    def ap_state(self):
        return AP_STATES.get(self.state, self.state)

    def similar(self, limit=10):
        from django.db import connections
        cursor = connections['ngrams'].cursor()
        cursor.execute("SELECT b FROM distance_bioguide WHERE a = %%s AND cosine_distance != 1 order by cosine_distance desc limit %s" % limit, [self.bioguide_id, ])
        results = []
        for result in cursor.fetchall():
            results.append(LegislatorRole.objects.filter(bioguide_id=result[0]).order_by('-end_date')[0])
        return results

    def current(self):
        return LegislatorRole.objects.filter(bioguide_id=self.bioguide_id, end_date__gte=datetime.date.today()).count() == 1


class ChangedBioguide(models.Model):
    old_bioguide_id = models.CharField(max_length=7, db_index=True)
    new_bioguide_id = models.CharField(max_length=7, db_index=True)
