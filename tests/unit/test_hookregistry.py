# -*- coding: utf-8 -*-

import threading

from tests.base import *

from radish.hookregistry import HookRegistry, before, after


class HookRegistryTestCase(RadishTestCase):
    """
        Tests for the HookRegistry class
    """
    def test_initializing_hook_registry(self):
        """
            Test the initialization of the hook registry
        """
        empty_hook = {"before": [], "after": []}

        hookregistry = HookRegistry()
        hookregistry.hooks.should.have.length_of(4)
        hookregistry.hooks["all"].should.be.equal(empty_hook)
        hookregistry.hooks["each_feature"].should.be.equal(empty_hook)
        hookregistry.hooks["each_scenario"].should.be.equal(empty_hook)
        hookregistry.hooks["each_step"].should.be.equal(empty_hook)

        HookRegistry.Hook.should.have.property("all")
        HookRegistry.Hook.should.have.property("each_feature")
        HookRegistry.Hook.should.have.property("each_scenario")
        HookRegistry.Hook.should.have.property("each_step")

    def test_register_as_hook(self):
        """
            Test registering function as hook
        """
        empty_hook = {"before": [], "after": []}

        hookregistry = HookRegistry()
        hookregistry.hooks.should.have.length_of(4)
        hookregistry.hooks["all"].should.be.equal(empty_hook)
        hookregistry.hooks["each_feature"].should.be.equal(empty_hook)
        hookregistry.hooks["each_scenario"].should.be.equal(empty_hook)
        hookregistry.hooks["each_step"].should.be.equal(empty_hook)

        hookregistry.hooks["all"]["before"].should.have.length_of(0)
        hookregistry.register("before", "all", "some_func")
        hookregistry.hooks["all"]["before"].should.have.length_of(1)
        hookregistry.hooks["all"]["after"].should.have.length_of(0)

        hookregistry.hooks["each_feature"]["before"].should.have.length_of(0)
        hookregistry.register("before", "each_feature", "some_func")
        hookregistry.hooks["each_feature"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_feature"]["after"].should.have.length_of(0)

        hookregistry.hooks["each_scenario"]["before"].should.have.length_of(0)
        hookregistry.register("before", "each_scenario", "some_func")
        hookregistry.hooks["each_scenario"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_scenario"]["after"].should.have.length_of(0)

        hookregistry.hooks["each_step"]["before"].should.have.length_of(0)
        hookregistry.register("before", "each_step", "some_func")
        hookregistry.hooks["each_step"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_step"]["after"].should.have.length_of(0)

    def test_decorating_with_hook(self):
        """
            Test decorating function as hook
        """
        hookregistry = HookRegistry()

        def some_func():
            pass

        hookregistry.hooks["each_feature"]["before"].should.have.length_of(0)
        before.each_feature(some_func)
        hookregistry.hooks["each_feature"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_feature"]["before"][0].should.be.equal(some_func)

        hookregistry.hooks["each_step"]["after"].should.have.length_of(0)
        after.each_step(some_func)
        hookregistry.hooks["each_step"]["after"].should.have.length_of(1)
        hookregistry.hooks["each_step"]["after"][0].should.be.equal(some_func)

    def test_calling_registered_hooks(self):
        """
            Test calling registered hooks
        """
        hookregistry = HookRegistry()

        data = threading.local()
        data.called_hooked_a = False
        data.called_hooked_b = False
        data.called_hooked_c = False

        def hooked_a():
            data.called_hooked_a = True

        def hooked_b():
            data.called_hooked_b = True

        def hooked_c():
            data.called_hooked_c = True

        before.each_feature(hooked_a)
        after.each_step(hooked_b)
        before.each_feature(hooked_c)

        hookregistry.call("before", "each_feature")
        data.called_hooked_a.should.be.true
        data.called_hooked_b.should.be.false
        data.called_hooked_c.should.be.true

        hookregistry.call("after", "each_step")
        data.called_hooked_a.should.be.true
        data.called_hooked_b.should.be.true
        data.called_hooked_c.should.be.true

    def test_calling_registered_hooks_with_arguments(self):
        """
            Test calling registered hooks with arguments
        """
        hookregistry = HookRegistry()

        data = threading.local()
        data.hooked_a_feature = None
        data.hooked_b_step = None
        data.hooked_c_feature = None

        def hooked_a(feature):
            data.hooked_a_feature = feature

        def hooked_b(step):
            data.hooked_b_step = step

        def hooked_c(feature):
            data.hooked_c_feature = feature

        before.each_feature(hooked_a)
        after.each_step(hooked_b)
        before.each_feature(hooked_c)

        hookregistry.call("before", "each_feature", "this is a feature")
        data.hooked_a_feature = "this is a feature"
        data.hooked_b_step = None
        data.hooked_c_feature = "this is a feature"

        hookregistry.call("after", "each_step", "this is a step")
        data.hooked_a_feature = "this is a feature"
        data.hooked_b_step = "this is a step"
        data.hooked_c_feature = "this is a feature"
