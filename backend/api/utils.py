import io

from django.db.models.aggregates import Sum
from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view


@api_view(['GET'])
def download_shopping_cart(request):
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
    pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
    x_position = 50
    y_position = 800

    shopping_cart = (
        request.user.shopping_cart.recipe.
        values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(
            amount=Sum('recipe__amount')).order_by()
    )

    page.setFont('Vera', 14)

    if shopping_cart:
        indent = 20
        page.drawString(x_position, y_position, 'Cписок покупок:')
        for index, recipe in enumerate(shopping_cart, start=1):
            page.drawString(
                x_position, y_position - indent,
                f'{index}. {recipe["ingredients__name"]} - '
                f'{recipe["amount"]}'
                f'{recipe["ingredients__measurement_unit"]}.'
            )
            y_position -= 15
            if y_position <= 50:
                page.showPage()
                y_position = 800
        page.save()
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shoppingcart.pdf')

    page.setFont('Vera', 24)
    page.drawString(
        x_position, y_position, 'Cписок покупок пуст!')
    page.save()
    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename='shoppingcart.pdf')
