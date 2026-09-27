import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Category } from '../interfaces/category.interface';

@Service()
export class CategoriesService {
    http = inject(HttpClient);
    // Categories API endpoint.
    apiUrl = 'http://localhost:3000/categories';

    // A fetch function that calls the endpoint to get all categories. 
    getAllCategories(): Observable<Category[]> {
        const categoriesData =  this.http.get<Category[]>(`${this.apiUrl}`);
        return categoriesData;
    }
}