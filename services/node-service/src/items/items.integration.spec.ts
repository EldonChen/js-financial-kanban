import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Test, TestingModule } from '@nestjs/testing';
import { MongooseModule } from '@nestjs/mongoose';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../app.module';
import { ItemsModule } from './items.module';
import { Item, ItemSchema } from './schemas/item.schema';

describe('ItemsController (e2e)', () => {
  let app: INestApplication;
  let createdItemId: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [
        MongooseModule.forRoot(
          process.env.MONGODB_URL || 'mongodb://localhost:27017',
          {
            dbName: 'test_financial_kanban',
          },
        ),
        MongooseModule.forFeature([{ name: Item.name, schema: ItemSchema }]),
        ItemsModule,
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('api/v1');
    await app.init();
  });

  afterAll(async () => {
    if (app) {
      await app.close();
    }
  });

  describe('/api/v1/items (POST)', () => {
    it('should create an item', () => {
      return request(app.getHttpServer())
        .post('/api/v1/items')
        .send({
          name: 'Test Item',
          description: 'Test Description',
          price: 99.99,
        })
        .expect(201)
        .expect((res) => {
          expect(res.body.code).toBe(200);
          expect(res.body.data.name).toBe('Test Item');
          createdItemId = res.body.data._id || res.body.data.id;
        });
    });

    it('should fail validation with missing required field', () => {
      return request(app.getHttpServer())
        .post('/api/v1/items')
        .send({
          description: 'Missing name',
        })
        .expect(400);
    });
  });

  describe('/api/v1/items (GET)', () => {
    it('should return all items', () => {
      return request(app.getHttpServer())
        .get('/api/v1/items')
        .expect(200)
        .expect((res) => {
          expect(res.body.code).toBe(200);
          expect(Array.isArray(res.body.data)).toBe(true);
        });
    });
  });

  describe('/api/v1/items/:id (GET)', () => {
    it('should return a single item', () => {
      return request(app.getHttpServer())
        .get(`/api/v1/items/${createdItemId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.code).toBe(200);
          expect(res.body.data._id || res.body.data.id).toBe(createdItemId);
        });
    });

    it('should return 404 for non-existent item', () => {
      return request(app.getHttpServer())
        .get('/api/v1/items/507f1f77bcf86cd799439011')
        .expect(404);
    });
  });

  describe('/api/v1/items/:id (PATCH)', () => {
    it('should update an item', () => {
      return request(app.getHttpServer())
        .patch(`/api/v1/items/${createdItemId}`)
        .send({
          name: 'Updated Item',
          price: 199.99,
        })
        .expect(200)
        .expect((res) => {
          expect(res.body.code).toBe(200);
          expect(res.body.data.name).toBe('Updated Item');
          expect(res.body.data.price).toBe(199.99);
        });
    });
  });

  describe('/api/v1/items/:id (DELETE)', () => {
    it('should delete an item', () => {
      return request(app.getHttpServer())
        .delete(`/api/v1/items/${createdItemId}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.code).toBe(200);
        });
    });

    it('should return 404 when deleting non-existent item', () => {
      return request(app.getHttpServer())
        .delete('/api/v1/items/507f1f77bcf86cd799439011')
        .expect(404);
    });
  });
});
