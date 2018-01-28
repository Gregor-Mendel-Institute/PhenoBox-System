import {ElementRef, HostListener, Directive} from '@angular/core';

@Directive({
  selector: 'textarea[textarea-autosize]'
})

export class TextareaAutosizeDirective {
  @HostListener('input', ['$event.target'])
  onInput(textArea: HTMLTextAreaElement): void {
    this.resize();
  }

  constructor(public element: ElementRef) {
  }

  ngAfterContentChecked(): void {
    this.resize();
  }

  resize(): void {
    this.element.nativeElement.style.overflow = 'hidden';
    this.element.nativeElement.style.height = 'auto';
    this.element.nativeElement.style.height = this.element.nativeElement.scrollHeight + "px";
  }
}
