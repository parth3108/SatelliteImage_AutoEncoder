<script lang="js">
	import '../app.css';
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import * as helper from '$lib/internal/helper/index.js';
	import { Satellite } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let sideBarActiveKey = helper.SideBarMenu[0].name;
	let sideBarActiveValue = helper.SideBarMenu[0];

	let subMenuActiveKey = '';

	onMount(() => {
		const path = $page.url.pathname;
		for (const side of helper.SideBarMenu) {
			if (path === '/') {
				sideBarActiveKey = 'Presentation';
				sideBarActiveValue = '';
				break;
			}

			if (side.path === path) {
				sideBarActiveKey = side.name;
				sideBarActiveValue = side;
				break;
			}
			if (side.subMenu) {
				for (const sub of side.subMenu) {
					if (sub.path === path) {
						sideBarActiveKey = side.name;
						sideBarActiveValue = side;
						subMenuActiveKey = sub.name;
						break;
					}
				}
			}
		}
	});
</script>

<Resizable.PaneGroup direction="horizontal" class="max-h-dvh min-h-dvh max-w-[100vw] border">
	<Resizable.Pane defaultSize={15} minSize={10}>
		<div class="flex h-full flex-col justify-start">
			<span class="flex h-14 items-center justify-center border-b text-[#e11d48]">
				<Satellite size="36" class="" />
			</span>
			{#each helper.SideBarMenu as side}
				<!-- svelte-ignore a11y-click-events-have-key-events -->
				<!-- svelte-ignore a11y-no-static-element-interactions -->
				<span
					class="m-1 flex cursor-pointer gap-4 rounded-md p-2 text-gray-700 hover:bg-[#e11d48] hover:text-white {side.name ===
					sideBarActiveKey
						? 'bg-[#e11d48] text-white'
						: ''}"
					on:click={() => {
						sideBarActiveKey = side.name;
						sideBarActiveValue = side;
						if (side.path) goto(side.path);
					}}
				>
					<svelte:component this={side.icon} />
					{side.name}
				</span>
			{/each}
		</div>
	</Resizable.Pane>
	{#if sideBarActiveKey !== 'Modules' && sideBarActiveKey !== 'Evaluation' && sideBarActiveKey !== 'Presentation'}
		<Resizable.Handle withHandle />
		<Resizable.Pane defaultSize={15} minSize={10}>
			<div class="flex h-full flex-col justify-start">
				<span class="flex h-14 items-center justify-between border-b pl-4 pr-8">
					<svelte:component this={sideBarActiveValue?.icon} size="24" />
					<span class="ml-2">{sideBarActiveValue?.name}</span>
				</span>

				{#if sideBarActiveValue === undefined || sideBarActiveValue.subMenu === undefined}
					<span class="flex h-full items-center justify-center p-6">
						<span class="font-semibold">No Sub Menu</span>
					</span>
				{:else}
					{#each sideBarActiveValue?.subMenu as subMenu}
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<span
							class="m-1 flex cursor-pointer gap-4 rounded-md p-2 text-gray-700 hover:bg-[#e11d48] hover:text-white {subMenu.name ===
							subMenuActiveKey
								? 'bg-[#e11d48] text-white'
								: ''}"
							on:click={() => {
								subMenuActiveKey = subMenu.name;
								goto(subMenu.path);
							}}
						>
							<svelte:component this={subMenu.icon} />
							{subMenu.name}
						</span>
					{/each}
				{/if}
			</div>
		</Resizable.Pane>
	{/if}
	<Resizable.Handle withHandle />
	<Resizable.Pane defaultSize={75}>
		<div class="h-full">
			<slot />
		</div>
	</Resizable.Pane>
</Resizable.PaneGroup>
