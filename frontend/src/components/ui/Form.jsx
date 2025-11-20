import { forwardRef } from 'react';
import { cn } from '@/utils/helpers';

/**
 * FormField Component
 * Wrapper for form fields with label and error display
 */
export const FormField = ({ label, error, required, children, className, htmlFor }) => {
  return (
    <div className={cn('space-y-1', className)}>
      {label && (
        <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      {children}
      {error && <p className="text-sm text-error-600">{error}</p>}
    </div>
  );
};

/**
 * FormInput Component
 * Text input field for forms
 */
export const FormInput = forwardRef(
  ({ label, error, required, className, leftIcon: LeftIcon, rightIcon: RightIcon, ...props }, ref) => {
    return (
      <FormField label={label} error={error} required={required} htmlFor={props.id || props.name}>
        <div className="relative">
          {LeftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <LeftIcon className="h-5 w-5 text-gray-400" />
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'block w-full rounded-md border-gray-300 shadow-sm transition-colors',
              'focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
              error && 'border-error-300 focus:border-error-500 focus:ring-error-500',
              LeftIcon && 'pl-10',
              RightIcon && 'pr-10',
              props.disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed',
              className
            )}
            {...props}
          />
          {RightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <RightIcon className="h-5 w-5 text-gray-400" />
            </div>
          )}
        </div>
      </FormField>
    );
  }
);

FormInput.displayName = 'FormInput';

/**
 * FormTextarea Component
 * Textarea field for forms
 */
export const FormTextarea = forwardRef(
  ({ label, error, required, className, rows = 4, ...props }, ref) => {
    return (
      <FormField label={label} error={error} required={required} htmlFor={props.id || props.name}>
        <textarea
          ref={ref}
          rows={rows}
          className={cn(
            'block w-full rounded-md border-gray-300 shadow-sm transition-colors',
            'focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            error && 'border-error-300 focus:border-error-500 focus:ring-error-500',
            props.disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed',
            className
          )}
          {...props}
        />
      </FormField>
    );
  }
);

FormTextarea.displayName = 'FormTextarea';

/**
 * FormSelect Component
 * Select dropdown for forms
 */
export const FormSelect = forwardRef(
  ({ label, error, required, className, options = [], placeholder, ...props }, ref) => {
    return (
      <FormField label={label} error={error} required={required} htmlFor={props.id || props.name}>
        <select
          ref={ref}
          className={cn(
            'block w-full rounded-md border-gray-300 shadow-sm transition-colors',
            'focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            error && 'border-error-300 focus:border-error-500 focus:ring-error-500',
            props.disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
      </FormField>
    );
  }
);

FormSelect.displayName = 'FormSelect';

/**
 * FormCheckbox Component
 * Checkbox input for forms
 */
export const FormCheckbox = forwardRef(
  ({ label, error, required, className, description, ...props }, ref) => {
    return (
      <div className={cn('space-y-1', className)}>
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              ref={ref}
              type="checkbox"
              className={cn(
                'rounded border-gray-300 text-primary-600 transition-colors',
                'focus:ring-primary-500 focus:ring-offset-0',
                error && 'border-error-300',
                props.disabled && 'bg-gray-50 cursor-not-allowed'
              )}
              {...props}
            />
          </div>
          {label && (
            <div className="ml-3 text-sm">
              <label htmlFor={props.id || props.name} className="font-medium text-gray-700 cursor-pointer">
                {label}
                {required && <span className="text-error-500 ml-1">*</span>}
              </label>
              {description && <p className="text-gray-500">{description}</p>}
            </div>
          )}
        </div>
        {error && <p className="text-sm text-error-600">{error}</p>}
      </div>
    );
  }
);

FormCheckbox.displayName = 'FormCheckbox';

/**
 * FormRadio Component
 * Radio input for forms
 */
export const FormRadio = forwardRef(
  ({ label, error, required, className, options = [], ...props }, ref) => {
    return (
      <FormField label={label} error={error} required={required}>
        <div className={cn('space-y-2', className)}>
          {options.map((option) => (
            <div key={option.value} className="flex items-center">
              <input
                ref={ref}
                type="radio"
                value={option.value}
                id={`${props.name}-${option.value}`}
                className={cn(
                  'border-gray-300 text-primary-600 transition-colors',
                  'focus:ring-primary-500 focus:ring-offset-0',
                  error && 'border-error-300',
                  props.disabled && 'bg-gray-50 cursor-not-allowed'
                )}
                {...props}
              />
              <label
                htmlFor={`${props.name}-${option.value}`}
                className="ml-3 text-sm font-medium text-gray-700 cursor-pointer"
              >
                {option.label}
              </label>
            </div>
          ))}
        </div>
      </FormField>
    );
  }
);

FormRadio.displayName = 'FormRadio';

/**
 * FormSwitch Component
 * Toggle switch for forms
 */
export const FormSwitch = forwardRef(
  ({ label, error, required, className, description, ...props }, ref) => {
    return (
      <div className={cn('space-y-1', className)}>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {label && (
              <label htmlFor={props.id || props.name} className="text-sm font-medium text-gray-700">
                {label}
                {required && <span className="text-error-500 ml-1">*</span>}
              </label>
            )}
            {description && <p className="text-sm text-gray-500">{description}</p>}
          </div>
          <button
            ref={ref}
            type="button"
            role="switch"
            aria-checked={props.checked}
            onClick={() => props.onChange && props.onChange({ target: { checked: !props.checked } })}
            className={cn(
              'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent',
              'transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              props.checked ? 'bg-primary-600' : 'bg-gray-200',
              props.disabled && 'opacity-50 cursor-not-allowed'
            )}
            disabled={props.disabled}
          >
            <span
              className={cn(
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0',
                'transition duration-200 ease-in-out',
                props.checked ? 'translate-x-5' : 'translate-x-0'
              )}
            />
          </button>
        </div>
        {error && <p className="text-sm text-error-600">{error}</p>}
      </div>
    );
  }
);

FormSwitch.displayName = 'FormSwitch';

/**
 * FormFileInput Component
 * File input for forms
 */
export const FormFileInput = forwardRef(
  ({ label, error, required, className, accept, multiple, onChange, ...props }, ref) => {
    return (
      <FormField label={label} error={error} required={required} htmlFor={props.id || props.name}>
        <div
          className={cn(
            'border-2 border-dashed border-gray-300 rounded-lg p-6 text-center',
            'hover:border-primary-400 transition-colors cursor-pointer',
            error && 'border-error-300',
            className
          )}
        >
          <input
            ref={ref}
            type="file"
            accept={accept}
            multiple={multiple}
            onChange={onChange}
            className="hidden"
            {...props}
          />
          <label htmlFor={props.id || props.name} className="cursor-pointer">
            <div className="text-sm text-gray-600">
              <span className="font-medium text-primary-600 hover:text-primary-500">
                Click to upload
              </span>
              {' '}or drag and drop
            </div>
            {accept && (
              <p className="text-xs text-gray-500 mt-1">
                {accept}
              </p>
            )}
          </label>
        </div>
      </FormField>
    );
  }
);

FormFileInput.displayName = 'FormFileInput';

export default {
  FormField,
  FormInput,
  FormTextarea,
  FormSelect,
  FormCheckbox,
  FormRadio,
  FormSwitch,
  FormFileInput,
};
