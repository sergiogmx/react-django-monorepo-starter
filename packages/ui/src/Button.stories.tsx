// Plain Component Story Format: works in Ladle today and in Storybook if we migrate.
import { Button } from './Button';

export default {
  title: 'Components / Button',
};

export const Primary = () => <Button>Save changes</Button>;

export const Secondary = () => <Button variant="secondary">Cancel</Button>;

export const Danger = () => <Button variant="danger">Delete item</Button>;

export const Small = () => <Button size="sm">Small button</Button>;

export const Disabled = () => <Button disabled>Not available</Button>;
