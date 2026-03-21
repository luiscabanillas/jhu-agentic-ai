"""Gradio app for a small hardware store billing workflow."""

from __future__ import annotations

import gradio as gr

from inventory import (
    add_to_cart,
    calculate_total,
    cart_choices,
    inventory_choices,
    remove_from_cart,
    render_cart,
)


def build_cart_outputs(cart: list[int], message: str, total_text: str | None = None):
    total_value = total_text if total_text is not None else f"${calculate_total(cart)}"
    selected_cart_value = 0 if cart else None
    return (
        cart,
        gr.update(choices=cart_choices(cart), value=selected_cart_value),
        render_cart(cart),
        message,
        total_value,
    )


def on_add_item(selected_item_id: int | None, cart: list[int]):
    updated_cart, message = add_to_cart(selected_item_id, cart)
    return build_cart_outputs(updated_cart, message)


def on_remove_item(selected_cart_index: int | None, cart: list[int]):
    updated_cart, message = remove_from_cart(selected_cart_index, cart)
    return build_cart_outputs(updated_cart, message)


def on_calculate_total(cart: list[int]):
    total = calculate_total(cart)
    return f"Total bill: ${total}"


with gr.Blocks(title="AI Inventory Billing App") as demo:
    gr.Markdown("# AI Inventory Billing App")
    gr.Markdown(
        "Select tools from inventory, add or remove them from the cart, "
        "and calculate the final bill."
    )

    cart_state = gr.State([])

    with gr.Row():
        inventory_dropdown = gr.Dropdown(
            choices=inventory_choices(),
            value=101,
            label="Select Tool from Inventory",
        )
        cart_dropdown = gr.Dropdown(
            choices=[],
            value=None,
            label="Select Tool from Current Cart",
        )

    with gr.Row():
        add_button = gr.Button("Add Tool")
        remove_button = gr.Button("Remove Tool")
        total_button = gr.Button("Calculate Total")

    cart_display = gr.Textbox(
        label="Cart Contents",
        value="Cart is empty.",
        lines=8,
        interactive=False,
    )
    action_message = gr.Textbox(
        label="System Message",
        value="Ready.",
        interactive=False,
    )
    total_output = gr.Textbox(
        label="Final Total",
        value="$0",
        interactive=False,
    )

    add_button.click(
        fn=on_add_item,
        inputs=[inventory_dropdown, cart_state],
        outputs=[
            cart_state,
            cart_dropdown,
            cart_display,
            action_message,
            total_output,
        ],
    )

    remove_button.click(
        fn=on_remove_item,
        inputs=[cart_dropdown, cart_state],
        outputs=[
            cart_state,
            cart_dropdown,
            cart_display,
            action_message,
            total_output,
        ],
    )

    total_button.click(
        fn=on_calculate_total,
        inputs=cart_state,
        outputs=total_output,
    )


if __name__ == "__main__":
    demo.launch()
