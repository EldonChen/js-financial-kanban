import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type ItemDocument = Item & Document;

@Schema({ timestamps: true })
export class Item {
  @Prop({ type: String, required: true, minlength: 1, maxlength: 100 })
  name: string;

  @Prop({ type: String, maxlength: 500, required: false })
  description?: string;

  @Prop({ type: Number, min: 0, required: false })
  price?: number;
}

export const ItemSchema = SchemaFactory.createForClass(Item);
