import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Test, TestingModule } from '@nestjs/testing';
import { ItemsController } from './items.controller';
import { ItemsService } from './items.service';
import { CreateItemDto } from './dto/create-item.dto';
import { UpdateItemDto } from './dto/update-item.dto';

describe('ItemsController', () => {
  let controller: ItemsController;
  let service: ItemsService;

  const mockItem = {
    _id: '507f1f77bcf86cd799439011',
    name: 'Test Item',
    description: 'Test Description',
    price: 99.99,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockItemsService = {
    create: vi.fn(),
    findAll: vi.fn(),
    findOne: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  };

  beforeEach(async () => {
    // 重置所有 mock
    vi.clearAllMocks();
    
    // 重新初始化 mock 方法
    mockItemsService.create = vi.fn();
    mockItemsService.findAll = vi.fn();
    mockItemsService.findOne = vi.fn();
    mockItemsService.update = vi.fn();
    mockItemsService.remove = vi.fn();
    
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ItemsController],
      providers: [
        {
          provide: ItemsService,
          useValue: mockItemsService,
        },
      ],
    }).compile();

    controller = module.get<ItemsController>(ItemsController);
    service = module.get<ItemsService>(ItemsService);
    
    // 确保 controller 有正确的 service 引用
    if (!controller['itemsService']) {
      (controller as any).itemsService = mockItemsService;
    }
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('create', () => {
    it('should create an item', async () => {
      const createItemDto: CreateItemDto = {
        name: 'Test Item',
        description: 'Test Description',
        price: 99.99,
      };

      vi.spyOn(service, 'create').mockResolvedValue(mockItem as any);

      const result = await controller.create(createItemDto);
      expect(service.create).toHaveBeenCalledWith(createItemDto);
      expect(result).toEqual(mockItem);
    });
  });

  describe('findAll', () => {
    it('should return an array of items', async () => {
      const items = [mockItem];
      vi.spyOn(service, 'findAll').mockResolvedValue(items as any);

      const result = await controller.findAll();
      expect(service.findAll).toHaveBeenCalled();
      expect(result).toEqual(items);
    });
  });

  describe('findOne', () => {
    it('should return a single item', async () => {
      vi.spyOn(service, 'findOne').mockResolvedValue(mockItem as any);

      const result = await controller.findOne('507f1f77bcf86cd799439011');
      expect(service.findOne).toHaveBeenCalledWith('507f1f77bcf86cd799439011');
      expect(result).toEqual(mockItem);
    });
  });

  describe('update', () => {
    it('should update an item', async () => {
      const updateItemDto: UpdateItemDto = {
        name: 'Updated Item',
        price: 199.99,
      };

      const updatedItem = { ...mockItem, ...updateItemDto };
      vi.spyOn(service, 'update').mockResolvedValue(updatedItem as any);

      const result = await controller.update(
        '507f1f77bcf86cd799439011',
        updateItemDto,
      );
      expect(service.update).toHaveBeenCalledWith(
        '507f1f77bcf86cd799439011',
        updateItemDto,
      );
      expect(result).toEqual(updatedItem);
    });
  });

  describe('remove', () => {
    it('should delete an item', async () => {
      vi.spyOn(service, 'remove').mockResolvedValue(undefined);

      await controller.remove('507f1f77bcf86cd799439011');
      expect(service.remove).toHaveBeenCalledWith('507f1f77bcf86cd799439011');
    });
  });
});
