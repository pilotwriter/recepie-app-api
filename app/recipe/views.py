from rest_framework import mixins,viewsets
from recipe import serializers
from core.models import Tag
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated





class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,mixins.CreateModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self,serializer):
        """create new tag"""
        serializer.save(user=self.request.user)
