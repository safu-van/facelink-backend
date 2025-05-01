import os
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings

from .serializers import PersonSerializer
from .utils import recognize_face
from facelink.couchbase_client import collection


class FindMissingPersonView(APIView):
    def post(self, request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data["image"]
            description = serializer.validated_data.get("description", "")
            timestamp = timezone.now().isoformat()

            # Save image locally
            image_name = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(settings.MEDIA_ROOT, image_name)
            with open(image_path, "wb+") as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Save to Couchbase
            doc_id = str(uuid.uuid4())
            doc_data = {
                "image_path": f"{settings.MEDIA_URL}{image_name}",
                "description": description,
                "timestamp": timestamp,
            }
            collection.upsert(doc_id, doc_data)

            # Face recognition
            match_result = recognize_face(image_path)

            if match_result["matched"]:
                return Response(
                    {
                        "message": "Person founded.",
                        "document_id": doc_id,
                        "match_frame": match_result["matched_image_url"],
                        "match_camera": match_result["camera"],
                        "matched_at": match_result["matched_at"],
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Person not founded.",
                        "document_id": doc_id,
                    },
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
