from django.core.exceptions import ValidationError
from django.db import models


# ----------------------------@amit--------------------------------
# Category Model
class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to='assets/category_logo/', blank=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Property to get the icon url
    @property
    def icon_url(self):
        return self.image.url if self.image else None

    # Property to get the category level
    @property
    def level(self):
        if self.parent:
            return self.parent.level + 1
        return 1

    # Property to get dict of category
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon_url,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get dict of category with parent
    @property
    def as_nested_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon_url,
            'description': self.description,
            'parent': self.parent.as_nested_dict if self.parent else None,
        }

    # Property to get min-dict of category
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon_url
        }

    # Property to get dict with list of children of category
    @property
    def as_dict_with_children(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon_url,
            'description': self.description,
            'children': [child.as_dict_min for child in self.children.all()]
        }

    # Property for displaying the category name
    @property
    def display_name(self):
        return f'{self.name} <-- {self.parent}' if self.parent else f'{self.name}'

    # Overriding the clean method
    def clean(self):
        if self.parent == self:
            raise ValidationError('Parent category can not be same as child category')

    def __str__(self):
        return f'{self.name} <-- {self.parent}' if self.parent else f'{self.name}'

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
