import inspect

from django.db import models
from django.core.exceptions import ValidationError, FieldDoesNotExist
from source.models import Source
from .model_decorators import combomethod


class ComplexField(models.Model):
    lang = models.CharField(max_length=5, null=False)
    sources = models.ManyToManyField(Source, related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True
        unique_together = ('object', 'lang')

    @combomethod
    def translate(self_cls, value, lang, object=None):
        if inspect.isclass(self_cls):
            cls = self_cls
            translations = cls.objects.filter(object=object)
        else:
            cls = self_cls.__class__
            translations = self_cls.__class__.objects.filter(object=object)

        translations = cls.objects.filter(object=object)
        if not translations.exists():
            raise FieldDoesNotExist("Can't translate a field that doesn't exist")

        translation = translations.filter(lang=lang)
        translation = list(translation[:1])
        if not translation:
            translation = cls()
            translation.object = object
            translation.lang = lang
        else:
            translation = translation[0]
            if translation.value != None:
                raise ValidationError("Can't translate an already translated field")

        translation.value = value
        translation.save()

        if hasattr(translation, 'sourced'):
            with_sources = cls.objects.exclude(sources=None)
            sources = with_sources[0].sources.all()
            for src in sources:
                translation.sources.add(src)

        translation.save()

    @combomethod
    def update(self_cls, value, lang, sources=[], object=None):
        if inspect.isclass(self_cls):
            cls = self_cls
            translations = cls.objects.filter(object=object)
        else:
            cls = self_cls.__class__
            translations = self_cls.__class__.objects.filter(object=object)

        for trans in translations:
            trans.value = None
            if hasattr(trans, 'sourced'):
                for source in sources:
                    trans.sources.clear()
            trans.save()
        translation = translations.filter(lang=lang)
        translation = list(translation[:1])
        if not translation:
            translation = cls()
            translation.object = object
            translation.lang = lang
        else:
            translation = translation[0]

        translation.value = value
        translation.save()

        if hasattr(translation, 'sourced'):
            for src in sources:
                translation.sources.add(src)
