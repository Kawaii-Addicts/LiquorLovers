from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import PartySerializer, PartyInvitationSerializer
from .models import Party, PartyInvitation

User = get_user_model()


class PartyViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Creates a new party object and associates the owner to the current user.
        """
        request.data['owner_public_id'] = request.user.public_id
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a party object if the user is allowed to see it.
        """
        party = self.get_object()

        if not party.can_see_party(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(party)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lists all the parties that a user can see.
        """
        queryset = filter(lambda p: p.can_see_party(request.user), self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def list_mine(self, request, *args, **kwargs):
        """
        Lists all the parties that the user is owner of.
        """
        queryset = request.user.parties_where_im_owner
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Updates a party. Returns a 403 Forbidden error if the request user is not the owner of the party.
        """
        if self.get_object().owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = request.data | {'owner_public_id': request.user.public_id}
        serializer = self.get_serializer(self.get_object(), data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates a party. Returns a 403 Forbidden error if the request user is not the owner of the party.
        """
        if self.get_object().owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes an existing party object if the user is the owner.
        """
        party = self.get_object()

        if party.owner != request.user and request.user not in party.participants.all():
            return Response(status=status.HTTP_403_FORBIDDEN)

        if party.owner != request.user:
            party.participants.remove(request.user)
            party.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        self.perform_destroy(party)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PartyInvitationViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    queryset = PartyInvitation.objects.all()
    serializer_class = PartyInvitationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles creation of party invitation or accepting party invitation.
        """
        party = self.get_party()

        if request.user != party.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data | {'party_public_id': party.public_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def accept(self, request, *args, **kwargs):
        """
        Handles the acceptance of a party invitation by the current user.
        """
        invitation = self.get_object()

        if request.user != invitation.receiver:
            return Response(status=status.HTTP_204_NO_CONTENT)

        invitation.accept()
        return Response(status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Retrieves the list of party invitations for the party.
        """
        party = self.get_party()

        if request.user != party.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset().filter(party=party)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_mine(self, request, *args, **kwargs):
        """
        Retrieves the list of party invitations for the current user.
        """
        queryset = self.get_queryset().filter(receiver=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of party invitation.
        """
        invitation = self.get_object()
        party = self.get_party()

        if request.user not in [party.owner, invitation.receiver]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(invitation)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_party(self):
        return get_object_or_404(Party, public_id=self.kwargs['party_public_id'])
