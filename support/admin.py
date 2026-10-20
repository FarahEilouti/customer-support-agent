
from django.contrib import admin

from support.models.support_ticket import SupportTicket
from support.models.conversation import Conversation
from support.models.message import Message
from support.models.agent_action import AgentAction
from support.models.faq_entry import FAQEntry
from support.models.order import Order


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "customer_email",
        "status",
        "priority",
        "created_at",
    )
    list_filter = ("status", "priority", "created_at")
    search_fields = ("title", "description", "customer_email")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("conversation",)

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    can_delete = False

    readonly_fields = ("role", "content", "created_at")
    fields = ("role", "content", "created_at")

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    inlines = [MessageInline]
    list_display = ("id", "customer_email", "created_at", "updated_at")
    search_fields = ("customer_email", "=id")
    readonly_fields = ("id", "created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "conversation__customer_email")
    readonly_fields = ("conversation", "role", "content", "created_at")
    list_select_related = ("conversation",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(AgentAction)
class AgentActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "tool_name",
        "success",
        "created_at",
    )
    list_filter = ("success", "tool_name", "created_at")
    search_fields = ("tool_name", "conversation__customer_email")
    readonly_fields = (
        "conversation",
        "tool_name",
        "arguments",
        "result",
        "success",
        "created_at",
    )
    list_select_related = ("conversation",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("support.view_agentaction")

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer")
    list_editable = ("is_active",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_email",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "customer_email")
    readonly_fields = ("created_at", "updated_at")