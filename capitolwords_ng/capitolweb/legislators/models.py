from django.db import models
from django.db.models import Q

from datetime import date


class State(models.Model):
    def __str__(self):
        return self.name

    short = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=25, unique=True)


class CongressPerson(models.Model):
    def __str__(self):
        return self.official_full
    bioguide_id = models.CharField(max_length=7, primary_key=True)
    first = models.CharField(max_length=25)
    middle = models.CharField(max_length=25)
    last = models.CharField(max_length=25)
    suffix = models.CharField(max_length=5)
    nickname = models.CharField(max_length=25)
    official_full = models.CharField(max_length=50)
    birthday = models.DateField(default=date(1776, 7, 4))
    gender = models.CharField(max_length=1, choices=(('M', "Male"), ('F', 'Female')))
    religion = models.CharField(max_length=30)

    @property
    def image_lg(self):
        return "https://theunitedstates.io/images/congress/450x550/{}.jpg".format(self.bioguide_id)

    @property
    def image_sm(self):
        return "https://theunitedstates.io/images/congress/225x275/{}.jpg".format(self.bioguide_id)

    class Meta:
        ordering = ('official_full',)


class Term(models.Model):
    def __str__(self):
        return "{} - {}".format(self.state, self.type)

    person = models.ForeignKey(CongressPerson, on_delete=models.CASCADE, related_name='terms')
    type = models.CharField(max_length=3, choices=(('sen', "Senate"), ('rep', 'House')))
    start_date = models.DateField()
    end_date = models.DateField()
    state = models.ForeignKey(State)
    district = models.IntegerField(default=-1)
    election_class = models.CharField(max_length=1)
    state_rank = models.CharField(max_length=6, choices=(('junior', 'junior'), ('senior', 'Senior')))
    party = models.CharField(max_length=25)
    caucus = models.CharField(max_length=25)
    address = models.TextField()
    office = models.TextField()
    phone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20)
    contact_form = models.URLField(blank=True, null=True)
    rss_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ('start_date',)


class ExternalId(models.Model):
    person = models.ForeignKey(CongressPerson, on_delete=models.CASCADE, related_name='external_ids')
    type = models.CharField(max_length=50)
    value = models.CharField(max_length=50)


def get_current_legislators(state=None):
    if state:
        people = CongressPerson.objects.filter(
            Q(terms__start_date__lte=date.today(), terms__end_date__gte=date.today(), terms__state=state))
    else:
        people = CongressPerson.objects.filter(
            Q(terms__start_date__lte=date.today(), terms__end_date__gte=date.today()))
    return people


