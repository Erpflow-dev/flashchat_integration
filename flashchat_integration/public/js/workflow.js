// FlashChat Workflow Management

frappe.provide("flashchat.workflow");

flashchat.workflow = {
    init: function() {
        this.setup_workflow_buttons();
        this.setup_workflow_dashboard();
    },

    setup_workflow_buttons: function() {
        // Add workflow test button to FlashChat Workflow form
        frappe.ui.form.on('FlashChat Workflow', {
            refresh: function(frm) {
                if (!frm.doc.__islocal && frm.doc.is_active) {
                    frm.add_custom_button(__('Test Workflow'), function() {
                        flashchat.workflow.test_workflow(frm);
                    });

                    frm.add_custom_button(__('View Logs'), function() {
                        frappe.set_route('List', 'FlashChat Workflow Log', {
                            'workflow': frm.doc.name
                        });
                    });

                    frm.add_custom_button(__('Clone Workflow'), function() {
                        flashchat.workflow.clone_workflow(frm);
                    });
                }

                // Add workflow statistics
                if (frm.doc.execution_count > 0) {
                    frm.dashboard.add_indicator(
                        __('Success Rate: {0}%', [frm.doc.average_success_rate || 0]), 
                        frm.doc.average_success_rate > 80 ? 'green' : 'orange'
                    );
                }
            },

            trigger_doctype: function(frm) {
                // Update recipient field options based on selected doctype
                if (frm.doc.trigger_doctype) {
                    frappe.model.with_doctype(frm.doc.trigger_doctype, function() {
                        let meta = frappe.get_meta(frm.doc.trigger_doctype);
                        let phone_fields = meta.fields.filter(f => 
                            f.fieldtype === 'Data' && 
                            (f.fieldname.includes('mobile') || f.fieldname.includes('phone'))
                        ).map(f => f.fieldname);

                        frm.set_df_property('recipient_field', 'description', 
                            'Available phone fields: ' + phone_fields.join(', '));
                    });
                }
            },

            message_template: function(frm) {
                if (frm.doc.message_template) {
                    frappe.db.get_value('Message Template', frm.doc.message_template, 'template_content')
                        .then(r => {
                            if (r.message && r.message.template_content) {
                                frm.set_value('custom_message', r.message.template_content);
                            }
                        });
                }
            }
        });
    },

    test_workflow: function(frm) {
        // Show dialog to select test document
        let dialog = new frappe.ui.Dialog({
            title: 'Test Workflow',
            fields: [
                {
                    fieldtype: 'Link',
                    fieldname: 'test_document',
                    label: 'Test Document',
                    options: frm.doc.trigger_doctype,
                    reqd: 1,
                    description: 'Select a document to test the workflow against'
                }
            ],
            primary_action_label: 'Test',
            primary_action: function(values) {
                frappe.call({
                    method: 'flashchat_integration.doctype.flashchat_workflow.flashchat_workflow.test_workflow',
                    args: {
                        workflow_name: frm.doc.name,
                        doc_name: values.test_document
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.msgprint(__('Workflow tested successfully!'));
                            dialog.hide();
                            frm.reload_doc();
                        } else {
                            frappe.msgprint(__('Workflow test failed: ') + (r.message.error || 'Unknown error'));
                        }
                    }
                });
            }
        });
        dialog.show();
    },

    clone_workflow: function(frm) {
        frappe.model.copy_doc(frm.doc);
        frappe.set_route('Form', 'FlashChat Workflow', 'new-flashchat-workflow-1');
    },

    setup_workflow_dashboard: function() {
        // Add workflow statistics to main dashboard
        if (frappe.get_route()[0] === 'desk') {
            this.create_workflow_widget();
        }
    },

    create_workflow_widget: function() {
        let widget_html = `
            <div class="widget" id="flashchat-workflow-widget">
                <div class="widget-head">
                    <h4>Active Workflows</h4>
                    <button class="btn btn-xs btn-primary" onclick="flashchat.workflow.show_workflow_manager()">
                        Manage
                    </button>
                </div>
                <div class="widget-body">
                    <div id="workflow-stats">Loading...</div>
                </div>
            </div>
        `;

        $('.page-content .row:first .col-lg-6:last').append(widget_html);
        this.load_workflow_stats();
    },

    load_workflow_stats: function() {
        frappe.call({
            method: 'flashchat_integration.utils.get_workflow_stats',
            callback: function(r) {
                if (r.message) {
                    let stats = r.message;
                    let stats_html = `
                        <div class="row">
                            <div class="col-xs-6">
                                <div class="stat-card">
                                    <h3>${stats.active_workflows}</h3>
                                    <p>Active Workflows</p>
                                </div>
                            </div>
                            <div class="col-xs-6">
                                <div class="stat-card">
                                    <h3>${stats.executions_today}</h3>
                                    <p>Executions Today</p>
                                </div>
                            </div>
                        </div>
                        <div class="progress" style="margin-top: 10px;">
                            <div class="progress-bar" style="width: ${stats.success_rate}%"></div>
                        </div>
                        <small>Success Rate: ${stats.success_rate}%</small>
                    `;
                    $('#workflow-stats').html(stats_html);
                }
            }
        });
    },

    show_workflow_manager: function() {
        frappe.set_route('List', 'FlashChat Workflow');
    },

    create_bulk_workflow: function() {
        let dialog = new frappe.ui.Dialog({
            title: 'Create Bulk Workflow',
            size: 'large',
            fields: [
                {
                    fieldtype: 'Link',
                    fieldname: 'doctype',
                    label: 'DocType',
                    options: 'DocType',
                    reqd: 1
                },
                {
                    fieldtype: 'Code',
                    fieldname: 'filters',
                    label: 'Filters (JSON)',
                    options: 'JSON',
                    reqd: 1,
                    default: '{"docstatus": 1}'
                },
                {
                    fieldtype: 'Section Break'
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'message_type',
                    label: 'Message Type',
                    options: 'SMS\nWhatsApp',
                    default: 'SMS',
                    reqd: 1
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'recipient_field',
                    label: 'Recipient Field',
                    reqd: 1,
                    default: 'mobile_no'
                },
                {
                    fieldtype: 'Text',
                    fieldname: 'message',
                    label: 'Message',
                    reqd: 1
                }
            ],
            primary_action_label: 'Execute',
            primary_action: function(values) {
                frappe.call({
                    method: 'flashchat_integration.workflow_engine.execute_bulk_workflow',
                    args: {
                        doctype: values.doctype,
                        filters: values.filters,
                        message_config: {
                            message_type: values.message_type,
                            recipient_field: values.recipient_field,
                            message: values.message
                        }
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            let results = r.message.results;
                            let success_count = results.filter(r => r.success).length;
                            frappe.msgprint(`Bulk workflow executed: ${success_count}/${results.length} messages sent successfully`);
                            dialog.hide();
                        } else {
                            frappe.msgprint('Bulk workflow failed: ' + (r.message.error || 'Unknown error'));
                        }
                    }
                });
            }
        });
        dialog.show();
    }
};

// Initialize on page load
$(document).ready(function() {
    if (frappe.boot.flashchat_settings) {
        flashchat.workflow.init();
    }
});
