/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 * Copyright (C) 2026 kyro
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include <mach/mach.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <libkern/OSCacheControl.h>
#include <syslog.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TARGET_IMAGE_NAME  "AppPredictionClient"
#define TARGET_OFFSET      0x1be13cULL
#define UNSLID_VA          0x1a4b6813cULL

static const uint32_t kReturnZeroStub[2] = {
    0xd2800000, // mov x0, #0
    0xd65f03c0  // ret
};

static uintptr_t get_target_address(void) {
    uint32_t count = _dyld_image_count();
    for (uint32_t i = 0; i < count; i++) {
        const char *name = _dyld_get_image_name(i);
        if (name && strstr(name, TARGET_IMAGE_NAME)) {
            intptr_t slide = _dyld_get_image_vmaddr_slide(i);
            const struct mach_header_64 *hdr = (const struct mach_header_64 *)_dyld_get_image_header(i);
            syslog(LOG_NOTICE, "[stub] Found %s at base %p (slide: %p)", TARGET_IMAGE_NAME, hdr, (void *)slide);
            return (uintptr_t)hdr + TARGET_OFFSET;
        }
    }
    intptr_t global_slide = _dyld_get_image_vmaddr_slide(0);
    syslog(LOG_WARNING, "[stub] %s image not yet listed; falling back to unslid VA + slide %p", 
           TARGET_IMAGE_NAME, (void *)global_slide);
    return UNSLID_VA + (uintptr_t)global_slide;
}

__attribute__((constructor))
static void init_app_prediction_stub(void) {
    syslog(LOG_NOTICE, "[stub] Initializing backboardd AppPredictionClient bypass...");
    uintptr_t target_va = get_target_address();
    if (!target_va) {
        syslog(LOG_ERR, "[stub] Failed to resolve target address");
        return;
    }
    mach_port_t task = mach_task_self();
    vm_size_t page_sz = vm_page_size;
    vm_address_t page_start = target_va & ~(page_sz - 1);
    vm_size_t patch_sz = sizeof(kReturnZeroStub);
    vm_size_t protect_len = ((target_va + patch_sz - page_start) + (page_sz - 1)) & ~(page_sz - 1);
    
    kern_return_t kr = vm_protect(task, page_start, protect_len, FALSE, 
                                  VM_PROT_READ | VM_PROT_WRITE | VM_PROT_COPY);
    if (kr != KERN_SUCCESS) {
        syslog(LOG_ERR, "[stub] vm_protect (RW) failed: %d", kr);
        return;
    }
    
    memcpy((void *)target_va, kReturnZeroStub, patch_sz);
    
    kr = vm_protect(task, page_start, protect_len, FALSE, 
                    VM_PROT_READ | VM_PROT_EXECUTE);
    if (kr != KERN_SUCCESS) {
        syslog(LOG_ERR, "[stub] vm_protect (RX) failed: %d", kr);
    }
    
    sys_icache_invalidate((void *)target_va, patch_sz);
    syslog(LOG_NOTICE, "[stub] Successfully stubbed function at %p with 'mov x0, #0; ret'", (void *)target_va);
}
