//conversation_service.py
import threading
import uuid
from collections import defaultdict

class ConversationService:
    def __init__(self):
        self.conversations = defaultdict(dict)
        self.lock = threading.Lock()

    # ========================================================
    # CREATE CONVERSATION
    # ========================================================
    def create_conversation(
        self,
        user_id,
        document_ids=None,
        document_names=None,
    ):
        conversation_id = str(uuid.uuid4())
        conversation = {
            "id": conversation_id,
            "user_id": user_id,
            "messages": [],
            # Documents actually used by the latest answer
            "current_document": None,
            "current_documents": [],
            # All documents available to this conversation
            "available_documents": (
                list(document_names or [])
            ),
            "available_document_ids": (
                list(document_ids or [])
            ),
            "current_topic": None,
            "last_question": None,
            "last_rewritten_question": None,
            "last_answer": None,
            "last_sources": [],
        }

        with self.lock:
            self.conversations[user_id][
                conversation_id
            ] = conversation
        return conversation

    # ========================================================
    # GET CONVERSATION
    # ========================================================
    def get_conversation(
        self,
        user_id,
        conversation_id,
    ):
        if not conversation_id:
            return None

        with self.lock:
            return (
                self.conversations
                .get(user_id, {})
                .get(conversation_id)
            )

    # ========================================================
    # GET OR CREATE CONVERSATION
    # ========================================================
    def get_or_create_conversation(
        self,
        user_id,
        conversation_id=None,
        document_ids=None,
        document_names=None,
    ):
        if conversation_id:
            conversation = self.get_conversation(
                user_id,
                conversation_id,
            )

            if conversation:
                return conversation

        return self.create_conversation(
            user_id=user_id,
            document_ids=document_ids,
            document_names=document_names,
        )

    # ========================================================
    # SET AVAILABLE DOCUMENTS
    # ========================================================
    def set_available_documents(
        self,
        user_id,
        conversation_id,
        document_ids=None,
        document_names=None,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return None

        with self.lock:
            if document_ids is not None:
                conversation[
                    "available_document_ids"
                ] = list(document_ids)

            if document_names is not None:
                conversation[
                    "available_documents"
                ] = list(document_names)
        return conversation

    # ========================================================
    # GET AVAILABLE DOCUMENTS
    # ========================================================
    def get_available_documents(
        self,
        user_id,
        conversation_id,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return []
        
        return list(
            conversation.get(
                "available_documents",
                [],
            )
        )

    # ========================================================
    # ADD MESSAGE
    # ========================================================
    def add_message(
        self,
        user_id,
        conversation_id,
        question,
        answer,
        sources=None,
        rewritten_question=None,
        document_names=None,
        topic=None,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return None

        sources = sources or []

        # ----------------------------------------------------
        # Determine documents used by this answer
        # ----------------------------------------------------
        source_documents = []
        for source in sources:
            filename = source.get(
                "filename"
            )

            if (
                filename
                and filename
                not in source_documents
            ):
                source_documents.append(
                    filename
                )

        # ----------------------------------------------------
        # Preserve explicitly supplied document names
        # ----------------------------------------------------
        if document_names:
            current_documents = []
            for filename in document_names:
                if (
                    filename
                    and filename
                    not in current_documents
                ):
                    current_documents.append(
                        filename
                    )
        else:
            current_documents = (
                source_documents
            )

        # ----------------------------------------------------
        # Current document
        # ----------------------------------------------------
        current_document = (
            current_documents[0]
            if current_documents
            else None
        )

        message = {
            "role": "user",
            "question": question,
            "rewritten_question": (
                rewritten_question
                if rewritten_question is not None
                else question
            ),
            "answer": answer,
            "documents": current_documents,
            "sources": sources,
        }

        with self.lock:
            conversation[
                "messages"
            ].append(message)

            conversation[
                "last_question"
            ] = question

            conversation[
                "last_rewritten_question"
            ] = (
                rewritten_question
                if rewritten_question is not None
                else question
            )

            conversation[
                "last_answer"
            ] = answer

            conversation[
                "last_sources"
            ] = sources

            conversation[
                "current_documents"
            ] = current_documents

            conversation[
                "current_document"
            ] = current_document

            if topic is not None:
                conversation[
                    "current_topic"
                ] = topic

            # ------------------------------------------------
            # If documents were supplied for this message,
            # merge them into the conversation's available
            # document list.
            # ------------------------------------------------
            if document_names:
                existing_documents = (
                    conversation.get(
                        "available_documents",
                        [],
                    )
                )

                for filename in document_names:
                    if (
                        filename
                        and filename
                        not in existing_documents
                    ):
                        existing_documents.append(
                            filename
                        )

                conversation[
                    "available_documents"
                ] = existing_documents
        return message

    # ========================================================
    # GET RECENT MESSAGES
    # ========================================================
    def get_recent_messages(
        self,
        user_id,
        conversation_id,
        limit=10,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return []

        messages = conversation.get(
            "messages",
            [],
        )

        return messages[-limit:]

    # ========================================================
    # GET LAST MESSAGE
    # ========================================================
    def get_last_message(
        self,
        user_id,
        conversation_id,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return None

        messages = conversation.get(
            "messages",
            [],
        )

        if not messages:
            return None

        return messages[-1]

    # ========================================================
    # GET CONTEXT
    # ========================================================
    def get_context(
        self,
        user_id,
        conversation_id,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return {
                "last_question": None,
                "last_rewritten_question": None,
                "last_answer": None,
                "current_document": None,
                "current_documents": [],
                "available_documents": [],
                "available_document_ids": [],
                "current_topic": None,
                "recent_messages": [],
            }

        return {
            "last_question": conversation.get(
                "last_question"
            ),

            "last_rewritten_question":
                conversation.get(
                    "last_rewritten_question"
                ),

            "last_answer": conversation.get(
                "last_answer"
            ),

            "current_document":
                conversation.get(
                    "current_document"
                ),

            "current_documents":
                list(
                    conversation.get(
                        "current_documents",
                        [],
                    )
                ),

            "available_documents":
                list(
                    conversation.get(
                        "available_documents",
                        [],
                    )
                ),

            "available_document_ids":
                list(
                    conversation.get(
                        "available_document_ids",
                        [],
                    )
                ),

            "current_topic":
                conversation.get(
                    "current_topic"
                ),

            "recent_messages":
                list(
                    conversation.get(
                        "messages",
                        []
                    )[-10:]
                ),
        }

    # ========================================================
    # UPDATE TOPIC
    # ========================================================
    def update_topic(
        self,
        user_id,
        conversation_id,
        topic,
    ):
        conversation = self.get_conversation(
            user_id,
            conversation_id,
        )

        if not conversation:
            return None

        with self.lock:
            conversation[
                "current_topic"
            ] = topic
        return conversation

    # ========================================================
    # CLEAR CONVERSATION
    # ========================================================
    def clear_conversation(
        self,
        user_id,
        conversation_id,
    ):
        with self.lock:
            user_conversations = (
                self.conversations.get(
                    user_id,
                    {}
                )
            )

            if conversation_id in user_conversations:
                del user_conversations[
                    conversation_id
                ]
                return True
        return False

# ============================================================
# GLOBAL CONVERSATION SERVICE
# ============================================================
conversation_service = ConversationService()
