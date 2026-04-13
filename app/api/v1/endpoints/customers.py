from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.customer import crud_customer, crud_customer_address
from app.schemas.customer import (
    CustomerCreate, CustomerRead, CustomerUpdate,
    CustomerAddressCreate, CustomerAddressRead, CustomerAddressUpdate,
)
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CustomerRead])
def list_customers(
    commerce_store_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_customer.count_filtered(db, commerce_store_id=commerce_store_id, status=status, search=search)
    items = crud_customer.get_multi_filtered(db, commerce_store_id=commerce_store_id, status=status, search=search, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_customer.create(db, obj_in=payload)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_customer.get(db, id=customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_customer.get(db, id=customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud_customer.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_customer.get(db, id=customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud_customer.remove(db, id=customer_id)


@router.get("/{customer_id}/addresses", response_model=list[CustomerAddressRead])
def list_addresses(customer_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_customer_address.get_by_customer(db, customer_id=customer_id)


@router.post("/{customer_id}/addresses", response_model=CustomerAddressRead, status_code=201)
def create_address(customer_id: int, payload: CustomerAddressCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    from app.models.customer import CustomerAddress
    obj = CustomerAddress(customer_id=customer_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{customer_id}/addresses/{address_id}", response_model=CustomerAddressRead)
def update_address(customer_id: int, address_id: int, payload: CustomerAddressUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_customer_address.get(db, id=address_id)
    if not obj or obj.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Address not found")
    return crud_customer_address.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{customer_id}/addresses/{address_id}", status_code=204)
def delete_address(customer_id: int, address_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_customer_address.get(db, id=address_id)
    if not obj or obj.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Address not found")
    crud_customer_address.remove(db, id=address_id)
