from django import template

from django_imgproxy.builder import imgproxy

register = template.Library()
register.simple_tag(imgproxy)
