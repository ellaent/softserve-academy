# from django.db.models.signals import post_save, pre_save
# from .models import User
# from django.dispatch import receiver
# from django.contrib.auth.models import Permission
#
#
# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         User.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     print("obj: ", instance.role)
#     permission = Permission.objects.get(name='Can add book')
#     user, created = User.objects.get_or_create(id=instance.id)
#     if not created:
#         if instance.role == 'moderator':
#             user.user_permissions.add(permission)
#             user.is_staff = True
#             print("staff: ", user.is_staff)
#         else:
#             user.user_permissions.clear()
#             user.save()
#         # user.save()
#     # else:
#     #     if not instance.has_perm('users.add_book'):
#     #       instance.user_permissions.remove('users.add_book')
