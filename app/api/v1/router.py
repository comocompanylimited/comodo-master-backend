from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    businesses,
    websites,
    mobile_apps,
    commerce_stores,
    categories,
    brands,
    products,
    customers,
    orders,
    discounts,
    imports,
    dashboard,
    cj_dropshipping,
    checkout,
    public_products,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(websites.router, prefix="/websites", tags=["Websites"])
api_router.include_router(mobile_apps.router, prefix="/mobile-apps", tags=["Mobile Apps"])
api_router.include_router(commerce_stores.router, prefix="/commerce-stores", tags=["Commerce Stores"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(discounts.router, prefix="/discounts", tags=["Discounts"])
api_router.include_router(imports.router, prefix="/imports", tags=["Imports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(cj_dropshipping.router, prefix="/cj", tags=["CJ Dropshipping"])
api_router.include_router(checkout.router, prefix="/checkout", tags=["Checkout"])
api_router.include_router(public_products.router, prefix="/store/products", tags=["Store"])
