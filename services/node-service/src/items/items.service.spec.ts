import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Test, TestingModule } from '@nestjs/testing';
import { getModelToken } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { ItemsService } from './items.service';
import { Item } from './schemas/item.schema';
import { CreateItemDto } from './dto/create-item.dto';
import { UpdateItemDto } from './dto/update-item.dto';
import { NotFoundException } from '@nestjs/common';

describe('ItemsService', () => {
  let service: ItemsService;
  let model: Model<Item>;

  const mockItem = {
    _id: '507f1f77bcf86cd799439011',
    name: 'Test Item',
    description: 'Test Description',
    price: 99.99,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockSave = vi.fn().mockResolvedValue(mockItem);
  const mockItemModel = function (data: any) {
    return {
      save: mockSave,
      ...data,
    };
  } as any;

  Object.assign(mockItemModel, {
    find: vi.fn().mockReturnValue({
      exec: vi.fn().mockResolvedValue([mockItem]),
    }),
    findOne: vi.fn(),
    findById: vi.fn().mockReturnValue({
      exec: vi.fn().mockResolvedValue(mockItem),
    }),
    findByIdAndUpdate: vi.fn().mockReturnValue({
      exec: vi.fn().mockResolvedValue(mockItem),
    }),
    findByIdAndDelete: vi.fn().mockReturnValue({
      exec: vi.fn().mockResolvedValue(mockItem),
    }),
  });

  beforeEach(async () => {
    // 重置所有 mock
    vi.clearAllMocks();
    mockSave.mockResolvedValue(mockItem);
    
    // 重新初始化 mockItemModel
    Object.assign(mockItemModel, {
      find: vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue([mockItem]),
      }),
      findOne: vi.fn(),
      findById: vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(mockItem),
      }),
      findByIdAndUpdate: vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(mockItem),
      }),
      findByIdAndDelete: vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(mockItem),
      }),
    });
    
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ItemsService,
        {
          provide: getModelToken(Item.name),
          useValue: mockItemModel,
        },
      ],
    }).compile();

    service = module.get<ItemsService>(ItemsService);
    model = module.get<Model<Item>>(getModelToken(Item.name));
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('create', () => {
    it('should create a new item', async () => {
      const createItemDto: CreateItemDto = {
        name: 'Test Item',
        description: 'Test Description',
        price: 99.99,
      };

      const result = await service.create(createItemDto);
      expect(mockSave).toHaveBeenCalled();
      expect(result).toEqual(mockItem);
    });
  });

  describe('findAll', () => {
    it('should return an array of items', async () => {
      const items = [mockItem];
      mockItemModel.find = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(items),
      });

      const result = await service.findAll();
      expect(result).toEqual(items);
    });

    it('should return an empty array when no items exist', async () => {
      mockItemModel.find = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue([]),
      });

      const result = await service.findAll();
      expect(result).toEqual([]);
    });
  });

  describe('findOne', () => {
    it('should return a single item', async () => {
      mockItemModel.findById = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(mockItem),
      });

      const result = await service.findOne('507f1f77bcf86cd799439011');
      expect(result).toEqual(mockItem);
    });

    it('should throw NotFoundException when item not found', async () => {
      mockItemModel.findById = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(null),
      });

      await expect(
        service.findOne('507f1f77bcf86cd799439011'),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe('update', () => {
    it('should update and return an item', async () => {
      const updateItemDto: UpdateItemDto = {
        name: 'Updated Item',
        price: 199.99,
      };

      const updatedItem = { ...mockItem, ...updateItemDto };
      mockItemModel.findByIdAndUpdate = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(updatedItem),
      });

      const result = await service.update(
        '507f1f77bcf86cd799439011',
        updateItemDto,
      );
      expect(result.name).toBe(updateItemDto.name);
      expect(result.price).toBe(updateItemDto.price);
    });

    it('should throw NotFoundException when item not found', async () => {
      const updateItemDto: UpdateItemDto = {
        name: 'Updated Item',
      };

      mockItemModel.findByIdAndUpdate = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(null),
      });

      await expect(
        service.update('507f1f77bcf86cd799439011', updateItemDto),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe('remove', () => {
    it('should delete an item', async () => {
      mockItemModel.findByIdAndDelete = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(mockItem),
      });

      await service.remove('507f1f77bcf86cd799439011');
      expect(mockItemModel.findByIdAndDelete).toHaveBeenCalledWith(
        '507f1f77bcf86cd799439011',
      );
    });

    it('should throw NotFoundException when item not found', async () => {
      mockItemModel.findByIdAndDelete = vi.fn().mockReturnValue({
        exec: vi.fn().mockResolvedValue(null),
      });

      await expect(
        service.remove('507f1f77bcf86cd799439011'),
      ).rejects.toThrow(NotFoundException);
    });
  });
});
