### FlashChat

Complete SMS, WhatsApp, and OTP integration for ERPNext using FlashChat.xyz API with real-time messaging, automated notifications, and comprehensive tracking.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app flashchat_integration


# FlashChat Integration - Complete Workflow System Summary

## 📋 **New DocTypes Added:**

### 1. **FlashChat Workflow**
- **Purpose**: Define automated messaging workflows
- **Features**: 
  - Event-based and scheduled triggers
  - Python condition evaluation
  - Message template integration
  - Success rate tracking
  - Advanced settings (retry, DND, working hours)

### 2. **FlashChat Workflow Log**
- **Purpose**: Track workflow execution history
- **Features**:
  - Detailed execution logs
  - Success/failure tracking
  - Error traceback storage
  - Performance analytics

## 🚀 **Pre-built Workflow Templates:**

### Sales & Orders
1. **Order Confirmation SMS** - Automatic confirmation when Sales Order is submitted
2. **Payment Received Notification** - SMS when payment is received
3. **Delivery Notification WhatsApp** - WhatsApp message when order is delivered
4. **Quotation Follow-up** - Follow-up SMS after quotation submission

### Customer Engagement
5. **Welcome New Customer** - Welcome WhatsApp message for new customers
6. **Lead Follow-up SMS** - Immediate follow-up for new leads
7. **Invoice Overdue Reminder** - Automated payment reminders
8. **Appointment Reminder** - Scheduled appointment notifications

## 🎯 **Workflow Engine Capabilities:**

### Event-Based Automation

# Example: Order Confirmation
{
    "trigger_doctype": "Sales Order",
    "trigger_event": "on_submit",
    "conditions": "doc.docstatus == 1 and doc.contact_mobile",
    "message": "Dear {customer_name}, your order {name} for {grand_total} has been confirmed!"
}


### Scheduled Workflows

# Example: Delayed Welcome Message
{
    "delay_duration": 1,
    "delay_unit": "Hours",
    "message": "Welcome to {company_name}! We're excited to serve you."
}


### Conditional Logic

# Example: Overdue Invoice Reminder
{
    "conditions": """
    doc.docstatus == 1 and 
    doc.outstanding_amount > 0 and 
    frappe.utils.getdate(doc.due_date) < frappe.utils.getdate()
    """
}


## 🛠 **Advanced Workflow Features:**

### 1. **Drip Campaigns**
javascript
// Create automated message sequences
flashchat.workflow.setup_drip_campaign([
    {message: "Welcome!", interval: {hours: 0}},
    {message: "How are you doing?", interval: {days: 3}},
    {message: "Special offer for you!", interval: {days: 7}}
]);


### 2. **Bulk Workflow Execution**
javascript
// Execute workflow for multiple documents
flashchat.workflow.execute_bulk_workflow("Customer", {
    "customer_group": "Retail",
    "creation": [">=", "2025-01-01"]
}, {
    "message_type": "WhatsApp",
    "message": "Thank you for being our valued customer!"
});


### 3. **Anniversary/Birthday Automation**

# Automatic birthday wishes
def setup_anniversary_reminders():
    # Schedules birthday messages for all contacts
    # Calculates next birthday and schedules WhatsApp message


## 📊 **Workflow Management Interface:**

### Dashboard Widget
- Active workflow count
- Daily execution statistics
- Success rate monitoring
- Quick workflow management

### Workflow Testing
- Test workflows against real documents
- Validate conditions and message rendering
- Preview message output before activation

### Analytics & Reporting
- Execution success rates
- Performance metrics
- Error tracking and debugging
- Workflow usage statistics

## 🔧 **Configuration Options:**

### Message Settings
- **Template Integration**: Use pre-built message templates
- **Custom Messages**: Create dynamic messages with field placeholders
- **Multi-Channel**: SMS, WhatsApp, or OTP delivery
- **Fallback Recipients**: Backup phone numbers

### Execution Controls
- **Rate Limiting**: Respect API limits
- **Working Hours**: Send only during business hours
- **Do Not Disturb**: Respect customer preferences
- **Retry Logic**: Automatic retry on failures

### Conditions & Filters
- **Python Conditions**: Advanced conditional logic
- **Document Filters**: Target specific document states
- **Field Validation**: Check required fields exist
- **Time-based Rules**: Execute based on dates/times

## 🚦 **Workflow Lifecycle:**

### 1. **Creation**

# Create workflow programmatically
workflow = frappe.get_doc({
    "doctype": "FlashChat Workflow",
    "workflow_name": "Custom Workflow",
    "trigger_doctype": "Lead",
    "trigger_event": "after_insert",
    "message_type": "SMS",
    "custom_message": "Thank you for your interest!"
})
workflow.insert()


### 2. **Execution**
- Automatic trigger on document events
- Condition evaluation
- Rate limit checking
- Message preparation and sending
- Result logging

### 3. **Monitoring**
- Real-time execution tracking
- Success/failure notifications
- Performance analytics
- Error debugging

## 🔗 **Integration Points:**

### ERPNext Document Events

# Automatic hooks for all document events
doc_events = {
    "*": {
        "after_insert": "execute_workflow_hooks",
        "on_submit": "execute_workflow_hooks",
        "on_cancel": "execute_workflow_hooks"
    }
}


### Scheduled Tasks

scheduler_events = {
    "hourly": ["process_scheduled_workflows"],
    "daily": ["cleanup_workflow_logs"],
    "weekly": ["generate_workflow_analytics"]
}


## 📱 **Frontend Enhancements:**

### Form Integration
- Workflow buttons on document forms
- Test workflow functionality
- Clone and modify workflows
- View execution logs

### List View Enhancements
- Workflow status indicators
- Bulk workflow execution
- Quick workflow creation
- Performance metrics display

## 🛡 **Security & Compliance:**

### Data Protection
- Condition validation and sandboxing
- Safe Python execution environment
- Input sanitization
- Error handling and logging

### Access Control
- Role-based workflow permissions
- User-specific workflow access
- Audit trail maintenance
- Secure API endpoints

## 🔄 **Workflow Examples:**

### E-commerce Automation

# Complete order lifecycle
workflows = [
    "Order Confirmation → Payment Reminder → Shipping Notification → Delivery Confirmation → Follow-up Survey"
]


### Lead Nurturing

# Lead conversion funnel
workflows = [
    "Welcome Message → Product Info → Demo Invitation → Follow-up → Closing"
]


### Customer Support

# Support ticket lifecycle
workflows = [
    "Ticket Created → Status Updates → Resolution → Satisfaction Survey"
]


## 📈 **Performance Optimization:**

### Efficient Execution
- Background job processing
- Queue management
- Resource optimization
- Error recovery

### Scalability
- Bulk processing capabilities
- Rate limiting compliance
- Memory efficient operations
- Database optimization

## 🎛 **Admin Controls:**

### Global Settings
- Enable/disable workflow engine
- Set global rate limits
- Configure working hours
- Manage DND preferences

### Monitoring Tools
- Execution dashboards
- Performance metrics
- Error tracking
- Usage analytics

This comprehensive workflow system transforms FlashChat Integration from a simple messaging tool into a powerful automation platform, enabling sophisticated customer communication strategies with minimal manual intervention!

## 🚀 **Getting Started with Workflows:**

### **Configure FlashChat Settings**
- Set API credentials
- Configure rate limits
- Enable services

### **Activate Pre-built Workflows**
- Go to FlashChat Workflow list
- Enable desired workflows
- Customize messages as needed

### **Create Custom Workflows**
- Use the workflow form
- Set triggers and conditions
- Test before activation

### **Monitor Performance**
- Check dashboard widgets
- Review execution logs
- Analyze success rates
- Optimize based on metrics

The workflow system is now ready to automate your customer communications across the entire business process lifecycle!

## Key Workflow Features Added:

### ✅ **Comprehensive Workflow Engine**
- Event-based triggers (insert, save, submit, cancel)
- Scheduled workflows with delays
- Conditional execution with Python conditions
- Multi-recipient support
- Rate limiting and DND respect

### ✅ **Pre-built Workflow Templates**
- Order confirmation SMS
- Payment notifications
- Delivery notifications
- Lead follow-ups
- Invoice reminders
- Welcome messages
- Quotation follow-ups
- Appointment reminders

### ✅ **Advanced Features**
- Workflow testing and cloning
- Detailed execution logging
- Success rate tracking
- Bulk workflow execution
- Drip campaigns
- Anniversary reminders

### ✅ **Management Interface**
- Workflow dashboard widget
- Statistics and analytics
- Test workflow functionality
- Workflow manager interface
- Execution log viewer

This workflow system provides a powerful automation framework for FlashChat integration, allowing users to create sophisticated messaging automations with minimal configuration!


### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

bash
cd apps/flashchat_integration
pre-commit install


Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
