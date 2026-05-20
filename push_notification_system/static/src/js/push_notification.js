/** @odoo-module **/

import { registry } from "@web/core/registry";

export const notificationService = {

    dependencies: ["bus_service", "notification"],

    start(env, { bus_service, notification }) {

        bus_service.addEventListener(
            "notification",
            ({ detail: notifications }) => {

                for (const { type, payload } of notifications) {

                    if (type === "simple_notification") {

                        notification.add(
                            payload.message || "",
                            {
                                title: payload.title || "Notification",
                                type: payload.type || "info",
                                sticky: payload.sticky || false,
                            }
                        );
                    }
                }
            }
        );

        return {};
    },
};

registry.category("services").add(
    "custom_notification_service",
    notificationService
);