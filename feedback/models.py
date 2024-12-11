from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.utils.text import slugify

class MartialArt(models.Model):
    martial_art_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(default='arts_pics/default.png', upload_to='arts_pics',blank=True)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        if not self.slug : 
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Movement(models.Model):
    movement_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    martial_art_id = models.ForeignKey(MartialArt, related_name="movements", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PracticeSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    movement_id = models.ForeignKey(Movement, related_name="practice_sessions", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='practice_sessions', on_delete=models.CASCADE)
    score = models.FloatField()
    user_feedback = models.TextField(blank=True, null=True)
    session_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.user.username} on {self.movement.name}"


class ProgressHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, related_name='progress_history', on_delete=models.CASCADE)
    movement_id = models.ForeignKey('Movement', related_name='progress_history', on_delete=models.CASCADE)
    progress_scores = models.JSONField(default=list)  # Use JSONField with a default value as an empty list

    def __str__(self):
        return f"Progress for {self.user_id.username} on {self.movement_id.name}"

    def add_progress(self, new_score):
        """Add a new score to the list of progress scores."""
        if isinstance(new_score, (int, float)):  # Ensure it's a number
            self.progress_scores.append(new_score)
            self.save()
        else:
            raise ValueError("Progress score must be a numeric value.")