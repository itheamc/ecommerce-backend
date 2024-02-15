from django.db import models


# ----------------------------@amit--------------------------------
# Supporting Information Model
class SupportingInformation(models.Model):
    title = models.CharField(max_length=100)
    description_en = models.TextField(max_length=2000, blank=True, null=True)
    description_np = models.TextField(max_length=2000, blank=True, null=True)
    summary = models.TextField(max_length=220, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Property to get the dict of supporting information
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'desc_en': self.description_en,
            'desc_np': self.description_np,
            'summary': self.summary,
        }

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Supporting Information'
        verbose_name_plural = 'Supporting Information'
